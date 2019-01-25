'''
   Copyright 2017 The Regents of the University of Colorado

   Licensed under the Apache License, Version 2.0 (the "License")
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
'''
 extract.py <db name> <username> <study_name> <extraction_id>
    - study name from the study table, indicating the input study
    - extraction id referring to a set of rows in categorization_function_metadata sharing the as-yet to be renamed study_id column
 Python Version: 3.6.3

 Extracts features data for feeding to ML. Closely related to categorization.py
 that calculates binned values and translates vocabulary values to values
 more readily used by machine learning algorithms like poLCA. For example,
 true and false typically end up in OHDSI as one of a pair of SNOMED concepts,
 but 1's and 2's work better in poLCA.

 This is research code for demonstration purposes only.

 croeder 6/2017 chris.roeder@ucdenver.edu
'''

import sys
import logging
import collections

import psycopg2
import psycopg2.extras
from HeartData import observation
from HeartData import categorization
from HeartData import migrate
import argh

from collections import OrderedDict
from HeartData.person import BasePerson
from HeartData.categorization import CategorizationRule
from HeartData.study import get_study_name
from HeartData.study import get_study_details
from HeartData.concepts import YES_EXTRACT_VALUE
from HeartData.concepts import NO_EXTRACT_VALUE
from HeartData.concepts import YES_EXTRACT_VALUE_01
from HeartData.concepts import NO_EXTRACT_VALUE_01

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name

OUTPUT_BASE = "/opt/local/harmonization/output"

class Extract(object):
    """ Extract extracts and categorizes values for use with ML alogorithms.
        It is a 1:1 mapping from concept types in OHDSI.observation to values
        here. Each such mapping may have one or more qualification associate with it,
        meaning that person must have certain attribute/value pairs. You could have
        different mappings for male and female for example.  Each mapping may also have
        parameters associated with it. The categoriazation functions take limit and rank
        values for example.
        This doesn't modify the database.
    """


    def __init__(self, con):
        self._con = con

    def _get_first_value(self, values_by_dates):
        dates = values_by_dates.keys()
        if dates:
            dates.sort()
            return values_by_dates[dates[0]]

        return None

    def _get_first_non_null_value(self, values_by_dates):
        dates = list(values_by_dates.keys())
        for value_date in dates:
            dates.sort()
            if values_by_dates[value_date] is not None:
                return values_by_dates[value_date]

        return None

    def flatten_person_values(self, person_values, person_id):
        """ Flattens a single person's values so there is only one value, per type,
            rather than possibly many values on different dates
            This selects the first value. TODO expand that with metadata to specify which to extract.
            Input: {(vocab, term) -> { date -> (string, number, concept)}}
            Output:  { (vocab, term) -> (string, number, concept) }
         """

        flat_values = {}
        for (vocab, term) in person_values:
            values_by_date = person_values[(vocab, term)]

            #flat_values[(vocab, term)] = _get_first_value(values_by_date)
            value_dict = self._get_first_non_null_value(values_by_date)
            if not value_dict:
                logger.warning("no values returned from  %s for %s", (vocab, term),  person_id)
            flat_values[(vocab, term)] =  value_dict

        return flat_values


    def rule_driven_melted_extraction(self, person_ids, extraction_id):
        """ For each person, for each rule, consider each observation/measurement/? (or look up more directly)
        and apply when the rule is apropriate (name of terms match and the qualifiers are true.

        Returns (values, names) where:
            values is a dictionary of dictionaries: id -> column -> value
            names is a dictionary of column -> name

        This is for the melted tables observation and measurement.
        """

        rules = categorization.CategorizationRule.load_rules(self._con, extraction_id)
        new_data_dict = collections.defaultdict(dict)
        names = {}
        concept_list = self._get_all_concepts()

        for person_id in person_ids:
            print("MELTED person:", person_id)
            # just the most recent values here, for now TODO
            # {(vocab, term) -> value}

            person_values = self._extract_person_values(person_id, concept_list)
            values = self.flatten_person_values(person_values, person_id)
            logger.debug("   VALUES: %s", person_values)
            for (long_name, rules_for_column) in rules.items():
                for rule in rules_for_column:
                    ####if rule.qualify(values) and rule.producesPositiveInteger(): # TODO really? (just a poor name) FIX CHRIS
                    if rule.qualify(values):
                        value = None
                        try:
                            value = rule.apply(values)
                            logger.debug("rule ran OK, COLUMN:%s, RULE: %s VALUE: %s person:%s values:%s", long_name, rule, value, person_id, person_values)
                        except Exception as  rule_exception:
                            logger.error("exception in rule:%s to person_id:%s, column:%s  type:%s  exception:%s", rule, person_id, long_name, type(rule_exception), rule_exception)
                        new_data_dict[person_id][long_name] = value
                    else:
                        logger.warn("DQ Rule: %s", rule) # TODO?
        for (long_name, rules_for_column) in rules.items():
            names[long_name] = rules_for_column[0].get_short_name()
        return (new_data_dict, names)


    def rule_driven_wide_extraction(self, person_ids, extraction_id):
        """ For each person, for each rule, consider each observation (or look up more directly)
        and apply when the rule is apropriate (name of terms match and the qualifiers are true.
        @ returns a dictionary of dictionaries: id -> column -> value
        This is for full-width tables like Death, visit_occurrence and procedure_occurrence.
        TODO Not using the function name attribute in the table for now...need to see how this evolves. I thought I would need it..
        Returns person_id -> long_name -> [value | None] 
        """

        new_data_dict = collections.defaultdict(dict)
        rules = categorization.CategorizationWideRule.load_rules(self._con, extraction_id)
        cur = self._con.cursor()
        for rule in rules:
            # TODO move this code to within the CategorizationWideRule
            if rule.specific_concept():
                # where-clause, like  you're interested in specific causes of death
                logger.info("Wide rule with where clause %s", rule)
                concept_id = migrate.get_concept_id(self._con, rule._from_vocabulary_id, rule._from_concept_code) # TODO private variables?
                for person_id in person_ids:
                    try:
                        # NB mixing formating some values into the query with a parameterized query in the execute() stmt.
                        statement = "SELECT {0} from {1} where person_id = %s and {2} = %s".format(rule._from_column, rule._from_table, rule._from_column) # field, table, field, concpet-id
                        cur.execute(statement, (person_id, concept_id,))
                        rows = cur.fetchall()
                        # old-school: boolean TODO what am I breaking here?
                        if rows:
                            value = rule.apply(rows[0][0])
                            new_data_dict[person_id][rule._long_name] =  value
                        else:
                            value = rule.apply(False)
                            new_data_dict[person_id][rule._long_name] =  value # XXX was an unmapped False
                    except:
                        logger.error("BAD QUERY: %s %s %s" , statement, rule._from_column, rule._from_table); 
            else:
                # no where-clause, any row will do, like all-cause death
                logger.info("Wide rule without where clause %s", rule)
                for person_id in person_ids:
                    try:
                        statement = "SELECT {0} from {1} where person_id = %s".format(rule._from_column, rule._from_table) # field, table, field, concpet-id
                        cur.execute(statement, (person_id,))
                        rows = cur.fetchall()
                        if rows:
                            value = rule.apply(rows[0][0])
                            new_data_dict[person_id][rule._long_name] =  value  # was True
                        else:
                            value = rule.apply(False)
                            new_data_dict[person_id][rule._long_name] =  value # XXXX was an un-mapped False
                    except:
                        logger.error("BAD QUERY: %s %s %s ", statement, rule._from_column, rule._from_table); 

        cur.close()
        return new_data_dict


    def extraction_header_test(self, rows):
        ''' test the extraction header TODO (obsolute?)'''
        terms = set()
        size = 0
        consistent = True
        for person_id in rows:
            for (vocab, term) in rows[person_id]:
                terms.add((vocab, term))
            if len(list(terms)) > size:
                if size != 0:
                    consistent = False
                size = len(list(terms))
        return consistent

    def print_extraction_header(self, melted_rows, wide_rows, names, outfile):
        ''' print the extraction header '''
        # MELTED
        # use the keys in order from the data (should be the same, but..)
        logger.info("print_extraction_header melted_rows length:%s wide_rows length:%s names:%s outfile:%s",
            len(melted_rows), len(wide_rows), names, outfile)
        person_id = list(melted_rows.keys())[0]
        outfile.write("{},".format("person_id"))
        #for long_name in sorted(melted_rows[person_id].keys()):
        for long_name in melted_rows[person_id].keys():
            outfile.write("{},".format(names[long_name].strip())) 


        # TABLE (CAST, WIDE) # TODO rename that stuff with wide rather than "table"
        #  {13002848L: {'Death': True, 'Hospitalization': False, 'CV Death 2': False, 'Non CV Death': False, 'Pump Failure': False, 'Transplant': False},
        logger.info("print_extraction_header wide_rows length:%s names:%s outfile:%s",
            len(wide_rows), names, outfile)
        if (len(wide_rows) > 0):
            prototype_row = wide_rows[list(wide_rows.keys())[0]]
            max_keys = len(prototype_row.keys())
            ## TODO for key in prototype_row.keys():
            for key in prototype_row:
                outfile.write("{},".format(key.strip()))

        outfile.write("study\n")

    def print_extraction_data(self, melted_rows, wide_rows, outfile, study_name):
        """ table rows come from tables Death, visit_occurrence, procedure_occurrence and are usually outcomes
            Returns a map of terms and how many non-NA values each has
        """
        na_dict = {}
        # TODO for (person_id) in melted_rows.keys():
        for person_id in melted_rows:
            outfile.write("{},".format(person_id))

            # NARROW/Melted
            num_columns = len(melted_rows[person_id])
            #for long_name in sorted(melted_rows[person_id].keys()):
            for long_name in melted_rows[person_id].keys():
                term = long_name
                value =  melted_rows[person_id].get(term)
                if value is None:
                    outfile.write("NA,")

                    if term not in na_dict:
                        na_dict[term] = 0
                else:
                    if isinstance(value, bool):
                        outfile.write("{},".format(str(int(value) + 1)))
                    elif isinstance(value, str):
                        outfile.write("{},".format(value))
                    else:
                        outfile.write("{},".format(str(int(value))))

                    if not term in na_dict:
                        na_dict[term] = 1
                    else:
                        na_dict[term] += 1

            # WIDE/cast
            num_columns = len(wide_rows[person_id].keys())
            for (term, value) in wide_rows[person_id].items():
                if value is None:
                    outfile.write("NA,")

                    if not term in na_dict:
                        na_dict[term] = 0
                else:
                    if isinstance(value, bool):
                        # boolean extraction hack from (T, F) to (1,2) TODO
                        if value:
                            #outfile.write(str(YES_EXTRACT_VALUE))
                            outfile.write(str(YES_EXTRACT_VALUE_01))
                        else:
                            #outfile.write(str(NO_EXTRACT_VALUE))
                            outfile.write(str(NO_EXTRACT_VALUE_01))
                    else:
                        if isinstance(value, int):
                            outfile.write(str(int(value)))
                        else:
                            outfile.write(str(value))

                    outfile.write(",")

                    if not term in na_dict:
                        na_dict[term] = 1
                    else:
                        na_dict[term] += 1

            outfile.write(study_name)
            outfile.write("\n")

        return na_dict

    def _get_all_concepts(self):
        """ Returns a list of triples [ (table, vocabuarly, concept) ] """
        stmt = (
            "SELECT DISTINCT 'observation', c.vocabulary_id, c.concept_code "
            "  FROM observation o, concept c "
            " WHERE  o.observation_concept_id = c.concept_id"
            " union "
            "SELECT DISTINCT 'measurement', c.vocabulary_id, c.concept_code "
            "  FROM measurement m, concept c "
            " WHERE  m.measurement_concept_id = c.concept_id"
            )
        # TODO this needs an order-by!!!
        cur = self._con.cursor()
        cur.execute(stmt)
        rows = cur.fetchall()
        return rows

    def _extract_person_values(self, person_id, concept_list):
        """ f(person_id, [ (table, vocabulary, term) ] )  ->   { (vocab, term) -> { date -> (number, string, concept) } }
            Returns a dictionary of dictionaries. (vocab,term) -> date (string, number, concept) for the given person.
            The key is a triple (vocabulary, term, date).
        """
        person = {}
        for (ohdsi_table, vocab, term) in concept_list:
            values_by_date = OrderedDict()
            values = observation.fetch(self._con, ohdsi_table, person_id, vocab, term) # TODO repatriate that entity layer attempt, use polymorphism for different tables?
            for (value_as_number, value_as_string, value_as_concept_id, date) in values:
# XXX you'll never hit that 'if' condition? There is a case where you don't get a null value back, but no row, nothing.
                if value_as_number is None and  value_as_string is None and value_as_concept_id is None:
                    logger.warning("'None' value (not mapped?) for vocab:%s, term:%s, date:%s, person:%s", vocab, term, date, person_id)
                values_by_date[date] = (value_as_number, value_as_string, value_as_concept_id)
            if values_by_date:
                # since we're looking in both measurement and observation tables, only want to populate when there really are values: don't want to overwrite a list of values with an empty one.
                person[(vocab, term)] = values_by_date
        return person


    def _init_stats(self, stats, long_name):
        stats[long_name] = {}
        stats[long_name]['n'] = 0
        stats[long_name]['sum'] = 0
        stats[long_name]['min'] = sys.maxsize
        stats[long_name]['max'] = 0
        stats[long_name]['concepts'] = {}
        stats[long_name]['num_rules'] = 0

    def _get_extraction_matrix_stats(self, matrix, extraction_id):
        """ get min/avg/max/n stats on the extraction matrix, with the ultimate goal of comparing
            these numbers against what we see in ohdsi
        """

        stats = {}

        categorization_rules = CategorizationRule.load_rules(self._con, extraction_id)
        #stmt = ("select function_name, long_name, rule_id, from_vocabulary_id, from_concept_code "
        for (person_id, person_values) in matrix.items():
            for (long_name, matrix_value)  in person_values.items():
                if long_name not in stats.keys():
                    self._init_stats(stats, long_name)
                stats[long_name]['n'] += 1
                rules = categorization_rules[long_name]
                ohdsi_value_as_matrix = None
                for rule in rules: # assumes only a single will qualify
                    stats[long_name]['term'] = rule._from_concept_code
                    stats[long_name]['vocab'] = rule._from_vocabulary_id
                    stats[long_name]['num_rules'] += 1
                    ohdsi_tuples = observation.fetch(self._con, rule._from_table, person_id, rule._from_vocabulary_id, rule._from_concept_code)
                    if not ohdsi_tuples:
                        logger.warning("get_stats()no entity for table:%s, person:%s, vocab:%s, concept:%s", rule._from_table, person_id, rule._from_vocabulary_id, rule._from_concept_code)
                    else:
                        (number, string, concept, _) = ohdsi_tuples[0]
                        ohdsi_value_tuple = (number, string, concept)
                        #if (rule.qualify(value_tuple) and rule.producesPositiveInteger()):  # GAH!! gut that whole idea of rule qualification!! TODO
                        ohdsi_value_as_matrix = rule.apply_tuple(ohdsi_value_tuple)
                        logger.debug("OHDSI:%s converted: %s MATRIX:%s", ohdsi_value_tuple, ohdsi_value_as_matrix, matrix_value)
                        if number is not None:
                            stats[long_name]['sum'] += number
                            if number < stats[long_name]['min']:
                                stats[long_name]['min'] = number
                            if number > stats[long_name]['max']:
                                stats[long_name]['max'] = number
                        elif concept is not None:
                            if concept in stats[long_name]['concepts'].keys():
                                stats[long_name]['concepts'][concept] += 1
                            else:
                                stats[long_name]['concepts'][concept] = 1
                        else:
                            logger.info("extract._get_extraction_matrix_stats(): not taking stats on this column %s as it is neither a number, nor a concept", long_name)

            # TODO, a little hacky using the function to discern the value type...
                if ohdsi_value_as_matrix != matrix_value:
                    logger.warning("missing value: long_name:%s, matrix value:%s,  ohdsi_value_as_matrix:%s ohdsi_tuple:%s person_id:%s",
                                   long_name, matrix_value, ohdsi_value_as_matrix, ohdsi_tuples, person_id)
        return stats

    def _verify_extraction_matrix(self, matrix, extraction_id):
        """ compare the extracted matrix back into OHDSI
            param: matrix as nested maps: person_id -> column -> value
            output: log messages describing errors
            TODO: do I care about dates here?
        """
        categorization_rules = CategorizationRule.load_rules(self._con, extraction_id)
        #stmt = ("select function_name, long_name, rule_id, from_vocabulary_id, from_concept_code "
        for (person_id, person_values) in matrix.items():
            for (long_name, matrix_value)  in person_values.items():
                rules = categorization_rules[long_name]
                ohdsi_value_as_matrix=None
                for rule in rules: # assumes only a single will qualify
                    ohdsi_tuples = observation.fetch(self._con, rule._from_table, person_id, rule._from_vocabulary_id, rule._from_concept_code)
                    if not ohdsi_tuples:
                        logger.warning("verify:no entity for table:%s, person:%s, vocab:%s, concept:%s", rule._from_table, person_id, rule._from_vocabulary_id, rule._from_concept_code)
                    else:
                        (number, string, concept, _) = ohdsi_tuples[0]
                        ohdsi_value_tuple = (number, string, concept)
                        #if (rule.qualify(value_tuple) and rule.producesPositiveInteger()):  # GAH!! gut that whole idea of rule qualification!! TODO
                        ohdsi_value_as_matrix = rule.apply_tuple(ohdsi_value_tuple)

                if ohdsi_value_as_matrix != matrix_value:
                    logger.warning("verify bogus: long_name:%s, matrix value:%s,  ohdsi_value_as_matrix:%s ohdsi_tuple:%s",
                                   long_name, matrix_value, ohdsi_value_as_matrix, ohdsi_tuples)



def main(db_name, user_name, study_name, extraction_id) :
    conn = psycopg2.connect(database=db_name, user=user_name)
    (study_id, observation_range_start, observation_range_end, _, _) = get_study_details(conn, study_name)
    extraction = Extract(conn)

    person_obj = BasePerson.factory(study_id)
    person_ids = person_obj.get_study_person_ids(conn)

    logger.info("extracting %d persons.", len(list(person_ids)))
    (melted_rows, column_names) = extraction.rule_driven_melted_extraction(person_ids, extraction_id)
    wide_rows = extraction.rule_driven_wide_extraction(person_ids, extraction_id)

    # VERIFY
    extraction._verify_extraction_matrix(melted_rows, extraction_id)


    # STATS
    # stat_type = [min, max, avg, n, sum, n_rules]
    # long_name -> stat_type -> value
    stats = extraction._get_extraction_matrix_stats(melted_rows, extraction_id)
    for to_column in stats:
        stats[to_column]['avg'] = float(stats[to_column]['sum']) / float(stats[to_column]['n'])

    # if min values is stil maxint, something's fishy:
    ### ? logger.warn("min with issues (min == maxint) ...probably a phenotype that doesn't have stats because it has few enough distinct values to fall under the \"instances\" group:")
    for (to_column, col_stats) in stats.items():
        if col_stats['min'] == sys.maxsize:
            logger.info("bad minimums: %s n:%s sum:%s min/avg/max:%s ", to_column, col_stats['n'], 
                    col_stats['sum'], (col_stats['min'], col_stats['avg'], col_stats['max']))


    for (to_column, col_stats) in stats.items():
        if col_stats['min'] != sys.maxsize:
            logger.info("ok minimum:%s n:%s sum:%s min/avg/max:%s ", to_column, col_stats['n'], 
                    col_stats['sum'], (col_stats['min'], col_stats['avg'], col_stats['max']))

    for to_column in stats:
        logger.info("STATSs: to_col:%s", to_column)
        for (concept, counts) in stats[to_column]['concepts'].items():
            logger.info("STATSs: col:%s vocab:%s term:%s concept:%s counts:%s", to_column, stats[to_column]['vocab'], 
                stats[to_column]['term'], concept, counts)


    # PRINT
    csv_file = open(OUTPUT_BASE + '/' + study_name.lower() + '.csv', 'w+')
    logger.info("starting to write file %s", csv_file)
    extraction.print_extraction_header(melted_rows, wide_rows, column_names, csv_file)
    logger.info("...header in %s", csv_file)
    na_columns = extraction.print_extraction_data(melted_rows, wide_rows, csv_file, study_name)
    ##os.close(csv_file)

    # NA SUMMARY
    logger.info("summary:num_columns:%s", len(na_columns))
    for (term, count) in na_columns.items():
        logger.info("summary %s, %s", term, count)


    conn.commit()
    conn.close()
