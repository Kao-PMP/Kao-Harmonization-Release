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
 calculate.py <db_name> <user_name> <study_name>
 Python Version: 3.6.3

 This module contains code for running functions to create calculated values.
 It assumes the input dataset has been loaded and migrated to OHDSI. It runs
 all functions associated with the study_id, reading input from OHDSI and writing
 output to OHDSI. This is driven by configuration data in tables
 ohdsi_calculation_function, ohdsi_calculation_argument that describe the sources
 and destinations for data. The name of the function in the database much match
 the name of the function in Python.

 NB because of the way the observation and measurement Ids are tracked here, not as a sequence or auto-increment,
 you can't really run more then one migrate script at a time.

 This is research code for demonstration purposes only.

 croeder 7/2017 chris.roeder@ucdenver.edu
'''

import importlib
import logging
import sys

from psycopg2.extras import RealDictCursor
from HeartData.person import BasePerson
from HeartData.study import get_study_details
from HeartData import calculate_functions

import psycopg2
import psycopg2.extras
import argh

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name


EPOCH_START_DEFAULT_DATE="1970-01-01"

class CalculatedFieldFunction(object):
    """For applying the calculation functions for creating calculated fields.
    This code gets and organizes the related metadata, fetches the inputs,
    calcuates the value and stores it.
    Uses tables ohdsi_calculation_function, ohdsi_calculation_argument
    """

    def __init__(self, con, study_id, name, to_vocabulary_id, to_concept_code):
        self._to_vocabulary_id = to_vocabulary_id
        self._to_concept_code = to_concept_code
        self._connection = con
        self._study_id = study_id
        self._function_name = name
        self._observation_number = self._get_max_observation_number() +1
        self._measurement_number = self._get_max_measurement_number() +1
        self._person_obj = BasePerson.factory(study_id)

        module_name = "HeartData.calculate_functions" # hard-coded for now #TODO
        i = importlib.import_module(module_name)
        self._function_ref = getattr(i, self._function_name)
        cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # reconcile with query in get_function_instances()  TODO
        cursor.execute(("SELECT to_vocabulary_id, to_concept_code, to_table, to_column "
                        "  FROM ohdsi_calculation_function "
                        " WHERE function_name = %s AND study_id = %s and to_vocabulary_id = %s and to_concept_code = %s"
                        " ORDER BY function_order"),
            (self._function_name, str(self._study_id), to_vocabulary_id, to_concept_code))
        rows = cursor.fetchall()
        if len(rows) > 1:
            logger.error("more than one row in CalculatedFieldFunction init for study:%d, name:%s",
                self._study_id, self._function_name)
            raise Exception("more than one row in CalculatedFieldFunction init for study:{}, name:{}".format(
                self._study_id, self._function_name))
        if not rows:
            logger.error("No definition found in  CalculatedFieldFunction init for study:%d, name:%s vocab:%s term:%s",
                self._study_id, self._function_name, to_vocabulary_id, to_concept_code)
            raise Exception("No definition found in  CalculatedFieldFunction init for study:{}, name:{} vocab:{} term:{}".format(
                self._study_id, self._function_name, to_vocabulary_id, to_concept_code))
        self._to_vocabulary_id = rows[0]['to_vocabulary_id']
        self._to_concept_code = rows[0]['to_concept_code']
        self._to_table = rows[0]['to_table']
        self._to_column = rows[0]['to_column']
        self._concept_id = self.get_concept_id(self._to_vocabulary_id, self._to_concept_code)
        self._argument_descriptions = self._get_function_argument_descriptions()
        cursor.close()

    def __str__(self):
        return "CalculatedFieldFunction: " + str(self._study_id) + ", " + self._function_name + ", " + str(self._observation_number) + ", " + str(self._function_ref) + ", " + self._to_vocabulary_id + ", " + self._to_concept_code + ", " + self._to_table


    def _get_function_argument_descriptions(self):
        """
            Returns a list of triples [(vocabulary_id, concept_code, from_table)] in the order they should be passed.
        """

        cursor = self._connection.cursor()
        stmt = ("SELECT vocabulary_id, concept_code, from_table "
                 " FROM ohdsi_calculation_argument "
                 "WHERE function_name = %s"
                 "  AND study_id = %s"
                 "  AND to_vocabulary_id = %s"
                 "  AND to_concept_code = %s"
                 "ORDER BY argument_order ")
        cursor.execute(stmt, (self._function_name, str(self._study_id), self._to_vocabulary_id, self._to_concept_code))
        tuples = cursor.fetchall()
        cursor.close()
        return tuples


    def get_concept_id(self, vocabulary, concept):
        """ Returns the pk of the concept table for the given concept_code and vocabulary_id
        where those are the vocabulary name and the id within that vocabulary
        """

        cur = self._connection.cursor(cursor_factory=RealDictCursor)
        stmt = "SELECT concept_id FROM concept WHERE concept_code = %s and vocabulary_id = %s"
        cur.execute(stmt, (concept, vocabulary))
        rows = cur.fetchall()
        cur.close()
        if rows:
            logger.info("returning %s concept_id from  vocab:%s concept:%s  self:%s", rows[0]['concept_id'], vocabulary, concept, self)
            return rows[0]['concept_id']
        else:
            logger.error("returning NULL concept_id from  vocab:\"%s\" concept:\"%s\"  self:%s", vocabulary, concept, self)
        return None


    def _get_function_argument_values(self, patient_id):
        """ Queries the observation table for the value of this argument for the given patient
            Returns a tuple of lists ([(value_as_string, value_as_number, value_as_concept_id)],[date])
        """
        values = []
        dates = []
        cursor = self._connection.cursor()
        for (vocabulary_id, concept_code, from_table) in self._argument_descriptions:
            rows=None
            if from_table == 'observation':
                stmt = ("SELECT observation_date, value_as_string, value_as_number, value_as_concept_id "
                    "  FROM observation o, concept c "
                    " WHERE o.person_id = %s"
                    "   AND o.observation_concept_id = c.concept_id "
                    "   AND c.vocabulary_id = %s"
                    "   AND c.concept_code = %s"
                    "   AND (value_as_string is not null or value_as_number is not null or value_as_concept_id is not  null)"
                    " order by observation_date") # TODO crude method for choosing wich value here
                cursor.execute(stmt, (str(patient_id), str(vocabulary_id), str(concept_code)))
                rows = cursor.fetchall()
            elif from_table == 'measurement':
                stmt = ("SELECT measurement_date, null, value_as_number, value_as_concept_id "
                    "  FROM measurement m, concept c "
                    " WHERE m.person_id = %s"
                    "   AND m.measurement_concept_id = c.concept_id "
                    "   AND c.vocabulary_id = %s"
                    "   AND c.concept_code = %s"
                    "   AND (value_as_number is not  null or value_as_concept_id is not null)"
                    " order by measurement_date") # TODO crude method for choosing which value here
                cursor.execute(stmt, (str(patient_id), str(vocabulary_id), str(concept_code)))
                rows = cursor.fetchall()
            elif from_table == 'death':
                if  concept_code == 'x' and vocabulary_id == 'x':  # TODO consider null here? ...but the index on the table won't allow it for now
                    stmt = ("SELECT death_date,  null, null, cause_concept_id "
                        "  FROM death d"
                        " WHERE d.person_id = %s")
                    cursor.execute(stmt, (patient_id,))
                    rows = cursor.fetchall()
                else:
                    stmt = ("SELECT death_date, null, null, cause_concept_id "
                        "  FROM death d, concept c"
                        " WHERE d.person_id = %s"
                        "   AND d.cause_concept_id = c.concept_id "
                        "   AND c.vocabulary_id = %s"
                        "   AND c.concept_code = %s")
                    cursor.execute(stmt, (patient_id, str(vocabulary_id), str(concept_code)))
                    rows = cursor.fetchall()
            else:
                logger.error("_get_function_argument_values(): table name not recognzied %s", from_table)

            if rows:
                if (len(rows) > 1) :
                    logger.info("DEV: ...we got more than a single row back in _get_function_argument_values for pid:%s from_table:%s %s, %s", 
                        patient_id, vocabulary_id, concept_code, rows)
                for row in rows:
                    (date, value_as_string, value_as_number, value_as_concept_id) = row
                    values.append((value_as_string, value_as_number, value_as_concept_id))
                    dates.append(date)
                    logger.debug("_get_function_argument_values(): %d %s", len(rows), stmt)
            else:
                logger.info("_get_function_argument_values(): no rows returned for  study:%s pid:%s  arg_desc:%s len:%d pair:%s %s %s    %s",
                             self._study_id, patient_id, str(self._argument_descriptions), len(self._argument_descriptions), vocabulary_id, concept_code, from_table, stmt)
                logger.warn("_get_function_argument_values(): No rows returned  for stmt:%s  (pid, vocab, concept)%s", stmt, (str(patient_id), str(vocabulary_id), str(concept_code)) )
        cursor.close()
        logger.debug("_get_function_argument_values() %s", values)
        return (values, dates)

    #TODO add a sequence or auto-increment to these id columns
    def _get_max_observation_number(self):
        ''' returns the maximum observation number from the table (TODO OBSOLETE) '''
        stmt = "SELECT max(observation_id) from observation"
        cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(stmt)
        rows = cursor.fetchall()
        cursor.close()
        return rows[0]['max']

    #TODO add a sequence or auto-increment to these id columns
    def _get_max_measurement_number(self):
        ''' returns the maximum measurement number from the table (TODO OBSOLETE) '''
        stmt = "SELECT max(measurement_id) from measurement"
        cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(stmt)
        rows = cursor.fetchall()
        cursor.close()
        return rows[0]['max']

    def _insert_function_value(self, person_id, visit_date, value, concept_id):
        """ inserts a value into the observation table by vocabulary_id and its concept_code.
            NB: Don't confuse concept_code and concept_id.
            In OHDSI's observation table, there is an indirection through the concept table keyed
            by concept_id, hence the odd name concept_code for the term or concept's id in the
            context of the vocabulary.
        """
        cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        obs_stmt = "INSERT into observation (observation_id, person_id, observation_concept_id, observation_date,"\
                 + self._to_column + ", observation_type_concept_id)" \
                 + "  VALUES (%s, %s, %s, %s, %s,%s)"
        meas_stmt = "INSERT into measurement (measurement_id, person_id, measurement_concept_id, measurement_date,"\
                 + self._to_column + ", measurement_type_concept_id)" \
                 + "  VALUES (%s, %s, %s, %s, %s,%s)"
        if self._to_table == 'measurement':
            logger.debug("calculate._insert_function_value() insert into meas. obs_id:%s person_id:%s value:%s concept_id:%s date:%s",
                self._measurement_number, person_id, value, concept_id, visit_date)
            cursor.execute(meas_stmt, (str(self._measurement_number), str(person_id), self._concept_id, visit_date, value, 38000278))
            self._measurement_number += 1
        elif self._to_table == 'observation':
            logger.debug("calculate._insert_function_value() insert into obs. obs_id:%s person_id:%s value:%s concept_id:%s date:%s",
                self._observation_number, person_id, value, concept_id, visit_date)
            cursor.execute(obs_stmt, (str(self._observation_number), str(person_id), self._concept_id, visit_date, value, 38000278))
            self._observation_number += 1

        cursor.close()


    def _run_function_for_person(self, person_id, concept_id):
        ''' runs a calculation function for a single person '''
        (input_values, dates) = self._get_function_argument_values(person_id)
        visit_date = EPOCH_START_DEFAULT_DATE
        if len(dates) > 0:
            visit_date = dates[0] # TODO, a little arbitrary. The values selected are the first non-null and here the date is the date that went with the first concept...

        # SIGNATURE 1 (dates, values)
        if self._function_name == 'concept_or_list' or self._function_name == 'sum' or self._function_name == 'eos_to_death_days' \
            or self._function_name == 'eos_days' or self._function_name == 'eos_death_min_days' or self._function_name == 'eos_death_max_days' \
            or self._function_name == 'death_days':  # TODO

            # TODO this should be an explicit attribute on the function
            output_value = self._function_ref(dates, input_values)
            if output_value is None or str(output_value) == "-1":
                logger.error("_run_function_for_person() returned None for person:%s, skipping insertion. , date:%s, arg:%s input:%s fname:%s",
                         person_id, visit_date, self._argument_descriptions, input_values, self._function_name)
            else:
                self._insert_function_value(person_id, visit_date, output_value, concept_id)

        # SIGNATURE 2
        elif len(input_values) == len(self._argument_descriptions):
                output_value = self._function_ref(dates, *input_values)
                if output_value is None or str(output_value) == "-1":
                    logger.error("_run_function_for_person() returned None for person:%s, skipping insertion. , date:%s, arg:%s input:%s fname:%s",
                             person_id, visit_date, self._argument_descriptions, input_values, self._function_name)
                else:
                    self._insert_function_value(person_id, visit_date, output_value, concept_id) 

        else:
            logger.error("_run_function_for_person() wrong number of values %s for study_id:%s person:%s concept:%s, date:%s, desc:%s, val:%s fname:%s dates:%s",
                         len(input_values), self._study_id, person_id, concept_id, visit_date, self._argument_descriptions,
                         input_values, self._function_name, dates)


    def run_function(self):
        ''' runs a fucntion over the set of all persons '''
        person_ids = self._person_obj.get_study_person_ids(self._connection)
        person_count = 0
        for person_id in person_ids:
            if person_count % 100 == 0:
                logger.info("run_function() name:%s count:%d concept:%s", self._function_name, person_count, self._concept_id)
            person_count += 1
            self._run_function_for_person(person_id, self._concept_id)


def calculate_all_functions(connection, study_id):
    ''' calculates all functions over all persons '''
    tuples = get_function_instances(connection, study_id)
    logger.info("Calculating study %d, with %d rules", study_id, len(tuples))
    for function_tuple in tuples:
        logger.info("Calculating function:%s study:%s name:%s vocab;%s term:%s", function_tuple, study_id, function_tuple[0], function_tuple[1], function_tuple[2])
        ccf = CalculatedFieldFunction(connection, study_id, function_tuple[0], function_tuple[1], function_tuple[2])
        ccf.run_function()


def get_function_instances(connection, study_id):
    cur = connection.cursor()
    cur.execute(("SELECT distinct function_name, to_vocabulary_id, to_concept_code, function_order "
                 "FROM ohdsi_calculation_function "
                 "WHERE study_id = %s "
                 "ORDER BY function_order"), (study_id,))
    key_tuples = cur.fetchall()
    cur.close()
    return key_tuples


def main(db_name, user_name, study_name) :

    logger.info("CALCULATE ARGS:%s %s %s", db_name, user_name, study_name)
    logger.info("connecting to %s  %s", db_name, user_name)
    con = psycopg2.connect(database=db_name, user=user_name)
    con.autocommit = True
    (study_id, observation_range_start, observation_range_end, _, _) = get_study_details(con, study_name)
    calculate_all_functions(con, study_id)

    update_stmt = 'UPDATE study set calculated=\'t\' where study_name=%s'
    update_cur = con.cursor()
    try:
        update_cur.execute(update_stmt, (study_name,) )
    except Exception as  e:
        logger.error("unable to mark %s as calculated: %s, %s",  study_name, e, update_stmt)
    con.close()
