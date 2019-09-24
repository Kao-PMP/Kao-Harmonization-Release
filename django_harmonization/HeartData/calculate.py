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
import traceback

from psycopg2.extras import RealDictCursor
from HeartData.person import BasePerson
from HeartData.study import get_study_details
from HeartData import calculate_functions
from ui.models import Concept

import psycopg2
import psycopg2.extras
import argh


logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name


EPOCH_START_DEFAULT_DATE="1970-01-01"

class CalculatedFieldFunction(object):
    """
        For applying the calculation functions for creating calculated fields.
        This code gets and organizes the related metadata, fetches the inputs,
        calcuates the value and stores it.
        Uses tables ohdsi_calculation_function, ohdsi_calculation_argument
    """

    def __init__(self, con, study_id, name, to_vocabulary_id, to_concept_code, module_name):

        if name is None:
            raise Exception("function in study {} for vocab:{} and concept:{} needs a non-None name", study_id, to_vocabulary_id, to_concept_code)
        if module_name is None:
            raise Exception("function {} in study {} for vocab:{} and concept:{}  needs a non-None module_name.", name, study_id, to_vocabulary_id, to_concept_code)

        self._to_vocabulary_id = to_vocabulary_id
        self._to_concept_code = to_concept_code
        self._connection = con
        self._study_id = study_id
        self._function_name = name
        self._module_name = module_name
        self._observation_number = self._get_max_observation_number() +1
        self._measurement_number = self._get_max_measurement_number() +1
        self._person_obj = BasePerson.factory_on_id(study_id)
        i = importlib.import_module(module_name)
        self._function_ref = getattr(i, self._function_name)
        cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # reconcile with query in get_function_instances()  TODO
        cursor.execute(("SELECT to_vocabulary_id, to_concept_code, to_table, to_column, expression "
                        "  FROM ohdsi_calculation_function "
                        " WHERE function_name = %s "
                        "   AND study_id = %s "
                        "   AND to_vocabulary_id = %s "
                        "   AND to_concept_code = %s"
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
        self._expression = rows[0]['expression']
        self._concept_id = Concept.objects.get(vocabulary_id=self._to_vocabulary_id, concept_code=self._to_concept_code).concept_id
        self._argument_descriptions = self._get_function_argument_descriptions()
        cursor.close()

    def __str__(self):
        return "CalculatedFieldFunction: " + str(self._study_id) + ", " + self._function_name + ", " + str(self._observation_number) + ", " + str(self._function_ref) + ", " + self._to_vocabulary_id + ", " + self._to_concept_code + ", " + self._to_table


    def _get_function_argument_descriptions(self):
        """
            Returns a list of triples [(vocabulary_id, concept_code, from_table)] in the order they should be passed.
        """

        cursor = self._connection.cursor()
        stmt = ("SELECT vocabulary_id, concept_code, from_table, argument_name "
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

    def _get_function_argument_values(self, patient_id):
        """ Queries the observation table for the value of this argument for the given patient
            Returns a tuple of lists ([(value_as_string, value_as_number, value_as_concept_id)],[date])
            The first is a list of triples, one triple for each input variable. It's a triple to deal with
            the different data types: string, number, concept. The second list is a list of dates that
            corresponds to the first. They are the date the datum was collected.
        """

        values = []
        dates = []
        names = []  
        i=1;
        stmt=''
        cursor = self._connection.cursor()
        for (vocabulary_id, concept_code, from_table, argument_name) in self._argument_descriptions:
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
                logger.debug("STMT-obs:%s   ARGS:%s", stmt, (str(patient_id), str(vocabulary_id), str(concept_code)))
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
                logger.debug("STMT-meas:%s   ARGS:%s", stmt, (str(patient_id), str(vocabulary_id), str(concept_code)))
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
                logger.debug("STMT-death = %s", stmt)
            elif from_table == 'dual' and vocabulary_id == 'dual':
                # TODO - this is twisted. In order to pass in constants, the concept_code is the value, rather than part of a join to go get the value
                # Issue #49 mentions the business about using the string 'null' to slip NULL values past the PK/FK limitations.
                # measurement date irrelevant
                #stmt = ("SELECT observation_date, value_as_string, value_as_number, value_as_concept_id "

                #NB: the calling function acts differently when the table is "dual". Instead of reading the 
                #value associated with (vocab_id, concept_code) in the named table (like observation), the 
                #concept_code is return. It's mind bending and meta because often the concept_code is rather a concept_id.
                #In this case you're matching concept IDs instead of values associated with concepts.
                # see #135, #77

                if concept_code == 'null':
                    logger.debug("DUAL-1 %s", concept_code)
                    stmt = "SELECT '2001-01-01', Null, Null, Null"
                    cursor.execute(stmt)
                else:
                    logger.debug("DUAL-2 %s", concept_code)
                    # we have these values, just running select to get them in the form returned by the database (result set?)
                    stmt = "SELECT '2001-01-01', %s, %s, %s"
                    #cursor.execute(stmt, ( str(concept_code), float(concept_code), int(concept_code) ))
                    cursor.execute(stmt, ( str(concept_code), float(concept_code), float(concept_code) ))
                rows = cursor.fetchall()
                logger.debug("STMT-dual = %s", stmt)

            else:
                logger.error("_get_function_argument_values(): table name not recognzied %s vocab:%s", from_table, vocabulary_id)

            logger.warning("_get_function_argument_values():  ARG #%d vocab:%s, code:%s, table:%s, name:%s ROWS:%s", i, vocabulary_id, concept_code, from_table, argument_name, len(rows)) 
            i = i+1

            if rows:
                if (len(rows) > 1) :
                    logger.info("DEV: ...we got more than a single row back in _get_function_argument_values for pid:%s from_table:%s %s, %s", 
                        patient_id, vocabulary_id, concept_code, rows)
                for row in rows[:1]: # CHRIS
                    (date, value_as_string, value_as_number, value_as_concept_id) = row
                    values.append((value_as_string, value_as_number, value_as_concept_id))
                    dates.append(date)
                    logger.debug("_get_function_argument_values(): %d %s", len(rows), stmt) 
                names.append(argument_name)
            else:
                values.append((None, None, None))
                dates.append('2001-01-01')
                names.append(argument_name)
                logger.debug("_get_function_argument_values(): no rows returned for  study:%s pid:%s  arg_desc:%s len:%d pair:%s %s %s    %s",
                             self._study_id, patient_id, str(self._argument_descriptions), len(self._argument_descriptions), vocabulary_id, concept_code, from_table, stmt)
        cursor.close()
        return (values, dates, names)

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

    def _delete_function_value_for_person(self, person_id, concept_id):
        cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if self._to_table == 'measurement':
            meas_stmt = 'DELETE from measurement where person_id=%s and measurement_concept_id=%s;'
            cursor.execute(meas_stmt, (str(person_id), concept_id))
        elif self._to_table == 'observation':
            obs_stmt = 'DELETE from observation where person_id=%s and observation_concept_id=%s;'
            cursor.execute(obs_stmt, (str(person_id), concept_id))
    
    def _insert_function_value(self, person_id, visit_date, value, concept_id):
        """ inserts a value into the observation table by vocabulary_id and its concept_code.
            NB: Don't confuse concept_code and concept_id.
            In OHDSI's observation table, there is an indirection through the concept table keyed
            by concept_id, hence the odd name concept_code for the term or concept's id in the
            context of the vocabulary.
        """
        try:
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
            else:
                logger.error("BAD TABLE %s", self._to_table) 
                raise Exception("BAD TABLE in _insert_function_value {}".format(self))
        except Exception as e:
            logger.error("RAISE: %s", e)
            if self._to_table == 'measurement':
                logger.error("  MEAS STMT: %s", meas_stmt);
            else:
                logger.error("  OBS STMT: %s", obs_stmt);
            logger.error("  person_id:%s concept:%s value:%s", person_id, self._concept_id, value)  
            cursor.close()
            raise e
    
        cursor.close()


       
 
    def _run_function_for_person(self, person_id, concept_id):
        ''' runs a calculation function for a single person '''


        logger.info("DOING-1 %s    %s", self._function_name, concept_id)

        ## GET DATA
        (input_values, dates, names) = self._get_function_argument_values(person_id)


        ## PROCESS
        if  (len(input_values) > 0 or self._function_name == 'true')\
            and (self._function_name == 'map_concept_id' \
                 or self._function_name == 'ranges_to_rank'  \
                 or (len(input_values) == len(names) and len(input_values) == len(self._argument_descriptions)) ):
            visit_date = EPOCH_START_DEFAULT_DATE
            if len(dates) > 0:
                visit_date = dates[0] # TODO, a little arbitrary. The values selected are 
                    # the first non-null and here the date is the date that went with the first concept...
            
            # SIGNATURE 1 (dates, values, names, expression) This form allows the 
            # function to take a variable number of arguments.
                # TODO this (being a member of this list issue #47)  should be an explicit attribute on the function
            if self._function_name == 'concept_or_list' \
                or self._function_name == 'concept_and_list' \
                or self._function_name == 'sum' \
                or self._function_name == 'eos_to_death_days' \
                or self._function_name == 'eos_days' \
                or self._function_name == 'eos_death_min_days' \
                or self._function_name == 'eos_death_max_days' \
                or self._function_name == 'death_days' \
                or self._function_name == 'corona_smoking_to_yesno'\
                or self._function_name == 'concept_to_int'\
                or self._function_name == 'ranges_to_rank'\
                or self._function_name == 'run_simple_eval'\
                or self._function_name == 'map_concept_id':


                try:
                    # different signatures...
                    if self._function_name == 'run_simple_eval':
                        logger.debug(" VARS SIGNATURE 1-B names:%s input_values:%s", names, input_values) 
                        output_value=None
                        for i in range(0, len(names)):
                            bogus_input_flag = False
                            if input_values[i][1] is None:
                                bogus_input_flag = True
                                break
                        if (not bogus_input_flag):
                            output_value = self._function_ref(dates, input_values, names,  expression=self._expression)
                            logger.info("....SIGNATURE 1-B person:%s concept_id:%s f:%s  out:%s,  expr:%s", 
                                person_id, concept_id, self._function_name,  output_value, self._expression)
                        else:
                            logger.warning("....SIGNATURE 1-B skipping function because of BOGUS input values to SIMPLE EVAL. person:%s concept_id:%s f:%s  out:%s,  expr:%s bougs:%s", 
                                person_id, concept_id, self._function_name,  output_value, self._expression, input_values)
                    else:
                        output_value = self._function_ref(dates, input_values, names, self._expression)
                except Exception as e:
                    logger.error("calculate.py _run_function_for_person  raised %s", e)
                    logger.error("  calculate.py self: %s", str(self))
                    logger.error("  calculate.py dates:%s input_values:%s names:%s expr:%s", 
                        str(dates), str(input_values), str(names), str(self._expression) )
                    (exc_type, exc_value, exc_traceback) = sys.exc_info()
                    traceback.print_tb(exc_traceback, limit=6, file=sys.stdout)
                    raise e
                if output_value is None or str(output_value) == "-1":
                    logger.warning(" returned None for person:%s, skipping insertion.  concept_id:%s, date:%s, arg:%s input:%s fname:%s",
                             person_id, concept_id, visit_date, self._argument_descriptions, input_values, self._function_name)
                else:
                    logger.info("inserting output:%s concept:%s function:%s", output_value, concept_id, self._function_name)
                    self._insert_function_value(person_id, visit_date, output_value, concept_id)
    
    
            # SIGNATURE 2  This form allows the function to take a specific list of arguments rather than a list.
            elif len(input_values) == len(self._argument_descriptions):
                    logger.info("....SIGNATURE 2 %s %s %s", person_id, concept_id, self._function_name)
                    output_value = self._function_ref(dates, *input_values)
                    if output_value is None or str(output_value) == "-1":
                        logger.warning("_run_function_for_person() returned None for person:%s, skipping insertion. , date:%s, arg:%s input:%s fname:%s",
                                 person_id, visit_date, self._argument_descriptions, input_values, self._function_name)
                    else:
                        logger.info("inserting output:%s concept:%s function:%s", output_value, concept_id, self._function_name)
                        self._insert_function_value(person_id, visit_date, output_value, concept_id) 
    
            else:
                logger.error("wrong number of values %s for study_id:%s person:%s concept:%s, date:%s, desc:%s, val:%s fname:%s dates:%s",
                             len(input_values), self._study_id, person_id, concept_id, visit_date, self._argument_descriptions,
                             input_values, self._function_name, dates)
        else:
            logger.error("no argument values")



    def run_function(self):
        ''' runs a fucntion over the set of all persons '''
        person_ids = self._person_obj.get_study_person_ids(self._connection)
        person_count = 0
        for person_id in person_ids:
            if person_count % 1000 == 0:
                logger.info(" name:%s count:%d concept:%s", self._function_name, person_count, self._concept_id)
            person_count += 1
            self._delete_function_value_for_person(person_id, self._concept_id)
            self._run_function_for_person(person_id, self._concept_id)


def calculate_all_functions(connection, study_id):
    ''' calculates all functions over all persons '''
    tuples = get_function_instances(connection, study_id)
    for function_tuple in tuples:
        ccf = CalculatedFieldFunction(connection, study_id, function_tuple[0], function_tuple[1], function_tuple[2], function_tuple[4])
        logger.info("Calculating function:%s study:%s name:%s vocab;%s term:%s FUN: %s", function_tuple, study_id, function_tuple[0], function_tuple[1], function_tuple[2], ccf)
        ccf.run_function()


def get_function_instances(connection, study_id):
    cur = connection.cursor()
    cur.execute(("SELECT distinct function_name, to_vocabulary_id, to_concept_code, function_order, module_name "
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
    logger.warning("CALCULATE complete")

    update_stmt = 'UPDATE study set calculated=\'t\' where study_name=%s'
    update_cur = con.cursor()
    try:
        update_cur.execute(update_stmt, (study_name,) )
    except Exception as  e:
        logger.error("unable to mark %s as calculated: %s, %s",  study_name, e, update_stmt)
        raise e
    con.close()
