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
 categorization.py
 Python Version: 3.6.3

 This module has code to extract a feature matrix from OHDSI.
 The features and calculations for binning or categorization are configured
 in tables: categorization_function_metadata, categorization_function_parameters,
 and categorization_function_qualification. (more below)

 Write queries in the style of PostgreSQL: with %s for parameters. Test code will
 convert that to ? for sqlite used there.

 BUG: The sort order of variables extracted/queried from PostgreSQL is different on linux vs macos.
      https://stackoverflow.com/questions/19967555/postgres-collation-differences-osx-v-ubuntu

 This is research code for demonstration purposes only.

 croeder 7/2017 chris.roeder@ucdenver.edu
'''

import sys
from datetime import datetime
import psycopg2
import psycopg2.extras
import logging
from HeartData import observation
import copy
import collections
from HeartData.concepts import YES_EXTRACT_VALUE
from HeartData.concepts import NO_EXTRACT_VALUE
from HeartData.concepts import YES_EXTRACT_VALUE_01
from HeartData.concepts import NO_EXTRACT_VALUE_01
from HeartData.events_mapping import NULL_PLACEHOLDER


# DB TABLES:
#
# categorization_function_metadata
#   describes a function and the logical column in the feature_matrix it's output goes to.
#   Unsurprisingly, a common function is named "identity." Parameters are values input to
#   the function that are identical for each patient. Values come from the patient. Parameters
#   define the bins when binning and the mapping when translating values from one domain to another.
#
# categorization_function_parameters
#   describes input parameters or arguments to the function and under what concept they
#   will be found. The assumption is we're doing all of this once per patient.
#
# categorization_function_qualification. (more below)
#   distinguishes which parameters a function should be run with. In some cases, anemia
#   for example, the bins are defined differently for women than men. The same function
#   is used in either case, but with a different set of parameters.

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)



# DROP: requirements about passing value through when its in a certain range?


# algorithm possibilities that need optimization:
# 1) query one row, calculate, insert, repeat (current)
# 2) query batch, calculate batch, insert batch, repeat as tuned/necessary
# 3) write the function in sql and speed things up by not round-tripping in and out of the database, rather modify in-place (speculation)


# tuple: (value_as_number, value_as_string, value_as_concept_id)
def IdentityStringFunction( _, value_tuple):
    return value_tuple[1]

def IdentityConceptIdFunction( _, value_tuple):
    return value_tuple[2]

def IdentityNumberFunction( _, value_tuple):
    return value_tuple[0]

# values is (string, number, concept)
# parameters is (value_limit, from_string, from_concept_id, rank), value_limit does double-duty as the from_integer, rank is the ouptut for this rule

def MapStringFunction(parameters, value_tuple):
    """
        parameters is a list of tuples
    """
    for (_, from_string, _, rank) in parameters:
        if (value_tuple[1] == from_string): 
            return rank

    logger.error("MapStringFunction() no matching parameters:%s, val:%s ", 
        parameters, value_tuple)
    return None


def MapConceptIdFunction(parameters, value_tuple):
    """
        parameters is a list of tuples
    """
    for (_, _, from_concept_id, rank) in parameters:
        if (value_tuple[2] == from_concept_id):
            return rank
    # no matching parameters in 3rd place: 4188539,  val:[(None, None, 4188540, 1), (None, None, 4188539, 2)], val:(Decimal('2'), None, None)

    logger.error("MapConceptIdFunction() no matching parameters in 3rd place: val:%s, parameters:%s   ",
        value_tuple, parameters)
    return None


def MapIntegerFunction(parameters, value_tuple):
    """
        parameters is a list of tuples
    """
    for (limit, _, _, rank) in parameters:
        if (value_tuple[0] == limit):
            return rank

    logger.error("MapIntegerFunction() no matching parameters:%s, val:%s ",
        parameters, value_tuple)
    return None


def RangesToRankDescendingFunction(parameters, value_tuple):
    """
        parameters is a list of tuples
        parameters is [(limit, string, concept_id,  rank)]
    """
    for (limit, _, _, rank) in parameters:
        if (limit == None): # interpret as infinity
            return rank
        elif (value_tuple[0] > float(limit)):
            return rank

    logger.error("desc: no matching parameters:%s, for value:%s", parameters, value_tuple)
    return None


def RangesToRankAscendingFunction(parameters, value_tuple):
    """ gets the person's value from values_dict for this rule, then ranks it by
        the list of limits in the parameters list and returns the associated rank.
        The last has a null limit. Last when ordered by rank increasing.

        parameters is [(limit, string, concept_id,  rank)]
        value  is from  values_dict[(self._from_vocabulary_id, self._from_concept_code)]
    """

    for (limit, _, _, rank) in parameters:
        logger.debug("RangesToRankAsc() value:%s limit:%s rank%s", value_tuple, limit, rank)
        if (limit == None): # interpret as infinity
            return rank
        elif (value_tuple[0] <= float(limit)):
            #print("RangesToRankAsc() returning rank.....value:", value_tuple, " limit:", limit, " --> rank:", rank)
            return rank

    logger.error("asc: no matching parameters %s, %s", parameters, value_tuple)
    return None


def IsNotNullFunction01(value):
    if value == None:
        logger.debug("IsNotNullFunction01() value:%s ret:%s", value, NO_EXTRACT_VALUE_01)
        return NO_EXTRACT_VALUE_01
    else:
        logger.debug("IsNotNullFunction01() value:%s ret:%s", value, YES_EXTRACT_VALUE_01)
        return YES_EXTRACT_VALUE_01

def IsNotNullFunction(value):
    if (value):
        logger.debug("IsNotNullFunction() yes value:%s ret:%s", value, YES_EXTRACT_VALUE)
        return YES_EXTRACT_VALUE
    else:
        logger.debug("IsNotNullFunction() no value:%s ret:%s", value, NO_EXTRACT_VALUE)
        return NO_EXTRACT_VALUE

def DeathDaysFunction(value):
    death_date = value #datetime.strptime(value, '%Y-%m-%d')
    rand_date  = datetime.strptime(xxx, '%Y-%m-%d')
    delta = death_date - rand_date.date();
    if value == None:
        logger.debug("DeathDaysFunction() value:%s ret:%s", value, delta.days)
        return delta.days
    else:
        logger.debug("DeathDaysFunction() value:%s ret:%s", value, delta.days)
        return delta.days


class CategorizationWideRule :
    """ Represents rows from table categorization_function_table. Intended for rules
        concerning extraction from the non-melted tables Death, visit_occurrene, procedure_occurrence.
        This is much simpler than how the CategorizationRule works (for now).
    """

    def _functionFactory(self, name):
        if (name == "is_not_null_01"):
            return IsNotNullFunction01;
        if (name == "is_not_null"):
            return IsNotNullFunction;
        if (name == "death_days"):
            return DeathDaysFunction;


    def __init__(self, connection, function_name, long_name, from_table, from_column, from_vocabulary_id, from_concept_code):
        self._connection = connection
        self._function_name = function_name
        self._long_name = long_name # the extraction matrix column name
        self._from_table = from_table # the table within ohdsi: measurement or observation
        self._from_column = from_column
        self._from_vocabulary_id = from_vocabulary_id # the name/id of the vocabulary: SNOMED or LOINC
        self._from_concept_code = from_concept_code # the concept's id within the scope of the vocabulary concept.concept_code, not concept.concept_id
        self._function = self._functionFactory(function_name)


    def __str__(self):
        string_rep = "WideRule name:" + self._function_name \
            + " function_name:" + self._function_name \
            + " long_name:" + self._long_name \
            + " from_table:" + self._from_table \
            + " from_column:" + self._from_column \
            + " from_vocab:" + str(self._from_vocabulary_id) \
            + " from_concept:" + str(self._from_concept_code)
        return string_rep


    def apply(self, value):
        retval = None
        if (self._from_concept_code != None and self._from_concept_code != 'x'): # TODO concept_id not nullable...
            retval = self._function(value)
            logger.info("CategorizationWideRule: input:%s, output:%s, rule:%s",  value, retval, self)
        else:
            retval = self._function(value)
            logger.warning("CategorizationWideRule: no concept code. input:%s, output:%s, rule:%s",  value, retval, self)
        return retval


    @staticmethod
    def load_rules(connection, extraction_id):
        """ queries the db for all the rules in a study, returning CategorizationWideRule objects"""

        cursor = connection.cursor()
        stmt = ("SELECT function_name, long_name, from_table, from_column, from_vocabulary_id, from_concept_code "
                "  FROM categorization_function_table " # TODO rename to categorization_function_wide
                " WHERE function_name != 'x' "
                "   AND extract_study_id = %s "
                "ORDER BY long_name") 

        cursor.execute(stmt, (extraction_id,) )
        rows = cursor.fetchall()
        cursor.close()
        rules = []
        for row in rows:
            categorization_rule = CategorizationWideRule(connection,
                                          row[0], row[1], row[2], row[3], row[4], row[5])
            rules.append(categorization_rule)
        return rules

    def specific_concept(self): 
        if (self._from_vocabulary_id == NULL_PLACEHOLDER or  self._from_concept_code == NULL_PLACEHOLDER):
            return False
        else:
            return True

    def is_complete(self): 
        val= (self._long_name != None and self._from_vocabulary_id != None and self._from_concept_code != None)
        if (not val):
            logger.warn("not complete XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX %s", self)
            return False
        return val
        

class CategorizationRule:
    """ Represents rows from table categorization_function_metadata and others. Intended for rules
        concerning extraction from the melted tables observation and measurement.
        Rule application only requires values from the source column/concept.
        Qualification, however, is about the rest of the person. Anemia for example has a few inputs, but gender, a qualifying value for the rules, is not part of an input
        # TODO, so far anemia is the only place rule qualification fits in (verify?), could do that one with one function that takes gender as input

        extraction_id       - identifies the analysis project using this extraction config. It's not the input study like BEST or PARADIGM, its the id in 
                                categorization_rule_metadate. Called extract_study_id in the database.
        function_name       - name of function in _functionFactory() that maps to function objects in this file
        long_name           - long name of the extracted value
        rule_id             - to distinguish two rules on the same inputs and outputs (Ex.Anemia for male an female has different calculations)
        from_vocabulary_id  - the vocabulary id to pair with the concept code below
        from_concept_code   - with vocabulary id, this is the value being extracted from the from_table below
        comment
        from_table          - the table we're extracting from
        short_name          - short name of the extracted value, used in header rows of CSV files
    """

    def _functionFactory(self, name):
        if (name == "map_integer"):
            return MapIntegerFunction
        if (name == "map_string"):
            return MapStringFunction
        if (name == "map_concept_id"):
            return MapConceptIdFunction
        elif (name == "identity_string"):
            return IdentityStringFunction
        elif (name == "identity_number"):
            return IdentityNumberFunction
        elif (name == "identity_concept_id"):
            return IdentityConceptIdFunction
        elif (name == "ranges_to_rank_asc"):
            return RangesToRankAscendingFunction
        elif (name == "ranges_to_rank_desc"):
            return RangesToRankDescendingFunction
        elif (name == "map_boolean_concept_to_1_2"):
            return MapBooleanConceptTo12
        else:
            logger.error("No CategorizationRule function named %s. Check the categorization_function_metadata table for %s", name, self)
            return None

    def producesPositiveInteger(self):
        """ Functions that produce output appropriate for poLCA output non-zero, positive integers.
            This function basically tells you if it's OK to use for that use-case # TODO the definition, or name here is confusing
        """
        # TODO keep this up-to-date
        return self._function_name != "identity_string"

    def __init__(self, connection,  function_name, long_name, rule_id, from_vocabulary_id, from_concept_code, from_table, short_name, extraction_id):
        self._parameters = []
        self._qualifiers = []
        self._connection = connection

        self._function_name = function_name
        self._long_name = long_name # the extraction matrix column name
        self._rule_id = rule_id
        self._from_vocabulary_id = from_vocabulary_id # the name/id of the vocabulary: SNOMED or LOINC
        self._from_concept_code = from_concept_code # the concept's id within the scope of the vocabulary concept.concept_code, not concept.concept_id
        self._from_table = from_table # the table within ohdsi: measurement or observation
        self._short_name = short_name
        self._query_parameters(function_name, long_name, rule_id, extraction_id)
        self._query_qualifiers(function_name, long_name, rule_id, extraction_id )
        self._function = self._functionFactory(function_name)
        self._extraction_id = extraction_id

    def __str__(self):
        string_rep = "(narrow) CategorizationRule name:" + self._function_name \
            + " to_col:" + str(self._long_name) \
            + " short:" + str(self._short_name) \
            + " rule_id:" + str(self._rule_id) \
            + " from_vocab:" + str(self._from_vocabulary_id) \
            + " from_concept:" + str(self._from_concept_code) \
            + " params:" + str(self._parameters) \
            + " qualifiers:" + str(self._qualifiers)
        return string_rep

    def get_short_name(self):
        return self._short_name


    def get_num_bins(self):
        return len(self._parameters)

    def qualify(self, values_dict):
        """ tells if the qualifiers all pass.
        values_dict is a dictionary keyed by (vocabulary, concept_id) pairs.
        """
        good = True
        for (vocabulary_id, concept_code, value_as_string, value_as_number, value_as_concept_id) in self._qualifiers:
            if ((vocabulary_id, concept_code) in set(values_dict.keys())):
                if (not (   (values_dict[(vocabulary_id, concept_code)] == value_as_string)
                         or (values_dict[(vocabulary_id, concept_code)] == value_as_number)
                         or (values_dict[(vocabulary_id, concept_code)] == value_as_concept_id))):
                    good = False
        return good

    def apply(self, values_dict):
        """ apply the related function with a dictionary of all values for a given patient/person """
        retval = None

        if (self._from_concept_code != None and self._from_concept_code != 'x'): # TODO fix that 'x'
            needed_key = (self._from_vocabulary_id, self._from_concept_code)
            if (needed_key in values_dict) :
                value_tuple = values_dict[needed_key]
                retval = self._function(self._parameters, value_tuple)
                #logger.warning("CategorizationRule.apply(): needed:%s, value:%s retval:%s  ", needed_key, value_tuple, retval)
            else:
                logger.warning("CategorizationRule.apply(): didn't have data (key not present) for key:%s     self:%s values_dict:%s", needed_key, self, values_dict)
                #logger.warning("CategorizationRule.apply(): didn't have data (key not present) for key:%s  ", needed_key)

        else:
            logger.info("no mapping %s  %s      %s", self._from_vocabulary_id, self._from_concept_code, self)
            retval = 99;

        return retval


    def apply_tuple(self, value_tuple):
        """ apply the related function with a specific value tuple (number, string, concept_id)  a given patient/person """
        retval = self._function(self._parameters, value_tuple)
        return retval

    @staticmethod
    def _fix_substitution_mark(query, cursor):
        fixed_query = query
        #if isinstance(cursor, psycopg2.extensions.cursor):
        #    query=query.replace("?","%s")
        #else:
        if not isinstance(cursor, psycopg2.extensions.cursor):
            fixed_query=query.replace("%s", "?")
        return fixed_query


    @staticmethod
    def _query_rules(connection, extraction_id):
        cursor = connection.cursor()
        stmt = ("SELECT function_name, long_name, rule_id, from_vocabulary_id, from_concept_code, from_table, short_name, extract_study_id, sequence "
                "FROM categorization_function_metadata "
                "WHERE extract_study_id = %s "
                "ORDER BY sequence")
               # "ORDER BY long_name")
        stmt = CategorizationRule._fix_substitution_mark(stmt, cursor)
        try:
            cursor.execute(stmt, (extraction_id,))
        except Exception as e:
            print("STMT:", stmt) 
            print("CUR:", cursor)
            print("CON:", connection)
            raise e
        rows = cursor.fetchall()
        cursor.close()
        return rows


    @staticmethod
    def load_rules(connection, extraction_id):
        """ queries the db for all the rules, returning CategorizationRule objects
            as a mutli-map keyed by long_name .
            Some long_name names (Ex. Anemia) have two rules differentiated by rule_id. In the
            case of Anemia, one is a calculation for males and another for females.
            long_name -> [ rule, rule',...]
        """

        rules = collections.defaultdict(list)
        metadata_rows = CategorizationRule._query_rules(connection, extraction_id)
        for row in metadata_rows:
            categorization_rule = CategorizationRule(connection,
                                                     row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            rules[row[1]].append(categorization_rule)

        return rules


    def _query_parameters(self, function_name, long_name, rule_id, extraction_id):
        """ Queries for the parameters portion of this instance of a categorization rule.
            Rows here play double-duty. Numerical values are ranked by range using the
            value_limit field. String values are ranked by exact value using the from_string
            field. Value_limit should be null in this case.
        """
        cursor = self._connection.cursor()
        stmt  = ("SELECT value_limit, from_string, from_concept_id, rank "
                 "FROM categorization_function_parameters "
                 "WHERE function_name = %s and long_name = %s and rule_id = %s "
                 "  AND extract_study_id = %s "
                 "ORDER by rank asc")
        stmt = CategorizationRule._fix_substitution_mark(stmt, cursor)
        cursor.execute(stmt, (function_name, long_name, rule_id, extraction_id))
        rows = cursor.fetchall()
        if (rows != None and len(rows) > 0):
            for row in rows:
                self._parameters.append(row)
        else:
            logger.error("_query_parameters: num_bins is zero: function_name:%s long_name:%s rule_id:%s extraction_id:%s %s", function_name, long_name, rule_id, extraction_id, stmt)
        cursor.close()


    def _query_qualifiers(self, function_name, long_name, rule_id, extraction_id):
        """ Queries for the qualifiers portion of this instance of a categorization rule.
            An observation must have values matching these in the OHDSI domain """
        # qualifiersKey: function_name, long_name, (rule_id)
        cursor = self._connection.cursor()
        stmt = ("SELECT vocabulary_id, concept_code, value_as_string, value_as_number, value_as_concept_id "
                "FROM categorization_function_qualifiers "
                "WHERE function_name = %s and long_name = %s and rule_id = %s"
                 "  AND extract_study_id = %s ")
        stmt = CategorizationRule._fix_substitution_mark(stmt, cursor)
        cursor.execute(stmt, (function_name, long_name, rule_id, extraction_id))
        self._qualifiers = cursor.fetchall()
        cursor.close()
