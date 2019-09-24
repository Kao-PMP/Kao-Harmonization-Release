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
 migrate.py
 Python Version: 3.6.3

 Migrates data from a study like BEST into OHDSI.
 According to a mapping defined in the db table study_to_ohdsi_mapping, 
 this script selects values from file/columns of the BEST study and 
 inserts them into the OHDSI observation table.

 Older versions batched columns on the same table together to reduce the 
 number of queries. That has been removed here (9/2017).
 It gets complicated when you include  where-clause values
 in situtations with more than one column and more than one where-clause value.
 At what point do you break apart the columns and the where-clause values?
 I have a situation where there is really only one column involved, but many
 rules, each with a different where clause. This contradicts a where clause
 that may apply to row selection for a group of columns together. Sometimes
 the lines in study_to_ohdsi_mapping should play together and share a where clause
 and other times the where clause should break them apart. Needs more detailed
 modelling. TODO later because it's an optimization, but it's nice to get modelling done.

 To re-run this script, delete data from observation, measurement, visit_occurrence, procedure_occurrence, death and person.

 This is research code for demonstration purposes only.

 croeder 6/2017 chris.roeder@ucdenver.edu
'''

import logging
import datetime 
import importlib
import sys
import re
import psycopg2
import traceback
from psycopg2.extras import RealDictCursor

from HeartData.person import  BasePerson
from HeartData.study import get_study_details
from ui.models import  Concept
from ui.models import  Study
from ui.models import  StudyToOhdsiMapping
from ui.models import  StudyMappingArguments
from HeartData import observation
from HeartData import events_mapping

#from django.forms.models import model_to_dict

logger = logging.getLogger(__name__)

MAPPING_NOT_USED='not_used'
IDENTITY_MAPPING='identity'
VALUE_AS_STRING='value_as_string'
VALUE_AS_NUMBER='value_as_number'
VALUE_AS_CONCEPT_ID='value_as_concept_id'
NULL_DATE='2001-01-01' # for inserting into observation things that don't have dates 



def insert_ohdsi(con, table_name, value_column_name, observation_number, person_id, visit_date, concept_id, value):
    """ Basically inserts a value into an OHDSI table. 
        Obvious except that the column names include the table name, 
        like observation_id and observation_concept_id for the observation table.
        value should be a string, number or concept_id (ID, not code)
    """
    if value is None:
        raise Exception("null value in insert_ohdsi()")
    insert_stmt = ('INSERT INTO ' + table_name + ' (' + table_name + '_id, person_id, ' + table_name + '_concept_id, ' + table_name + '_date, ' +  value_column_name + ', ' + table_name + '_type_concept_id )'
                  ' VALUES (%s, %s, %s, %s, %s, %s)') # TODO consider alternate to liberal use of string conversion
    insert_cur = con.cursor()
    try:
        logger.debug("Value %s", value)
        logger.debug("STMT %s", insert_stmt)
        logger.debug("VALUES %s, %s, %s, %s, %s, %s", str(observation_number), person_id, str(concept_id), visit_date, value, str(38000278))
        insert_cur.execute(insert_stmt,  (str(observation_number), person_id, str(concept_id), visit_date, value, str(38000278))) # TODO consider alternate to liberal use of string conversions
    except Exception as  e:
        logger.error("throw in insert_ohdsi() %s ", (observation_number, person_id, concept_id, visit_date, value, 38000278), )
        logger.error("....%s", insert_stmt)
        logger.error("... %s", e)
        raise e;
    insert_cur.close()



def _map_column_value(mapping, value, arguments, con):
    ''' 
        param mapping - a StudyToOhdsiMapping object
        param value - a single value of either number, string, or concept_id (??) type
        param arguments - a StudyMappingArguments object
        param con - a database connection
        call a function named in row_data to transform the given value 
        mapping is a StudyToOhdsiMapping object
    '''

    if (mapping.function_name != None and mapping.function_name != MAPPING_NOT_USED):
        if (mapping.function_name != IDENTITY_MAPPING ):
            try:
                module_name = "HeartData.migrate_functions" # hard-coded for now #TODO
                imported_lib = importlib.import_module(module_name)
                f = getattr(imported_lib, mapping.function_name)

                # ** CALL OUT TO THE FUNCTION: **
                new_value = f(value, mapping, arguments, con); 

                logger.info("migrate._map_column_value() module:%s function:%s value:%s NEW VALUE:%s  ", 
                module_name, mapping.function_name, value, new_value )
                return new_value
            except Exception as e:
                logger.exception(e)
                raise e
        else:
            return value
    else:
        return None



# from_table, from_column, from_where_clause, from_where_column,  has_date
# driven by a Django object: mapping_obj
def select_values(mapping_obj, personObj, person_ids, value_cursor) :
    mapping_dict = {}

    mapping_dict["from_table"] = 'booger'
    mapping_dict["from_table"] = mapping_obj.from_table
    mapping_dict["from_column"]=mapping_obj.from_column
    mapping_dict["from_where_clause"]=mapping_obj.from_where_clause
    mapping_dict["from_where_column"]=mapping_obj.from_where_column
    mapping_dict["has_date"]=mapping_obj.has_date 
    return select_values_from_dict(mapping_dict, personObj, person_ids, value_cursor)

# driven by a dict: mapping
def select_values_from_dict(mapping, personObj, person_ids, value_cursor) :

    """ Selects values from study tables.
        Mapping has keys from_table, from_column, optionally from_where_clause, from_where_column, has_date
        Returns value_rows with fields id_column_name, from_column, optionally date_value, 
    """
    logger.debug("select_values() starting...")

    #if mapping.from_table == 'dual':
    if mapping['from_table'] == 'dual':
        # Oracle and MySQL style dummy table
        value_rows=[]
        #logger.info("migrate select_values() starting...%s", person_ids)
        logger.info("migrate select_values() starting dual...")
        for person_id in person_ids:
            try:
                logger.debug("ZZZselect_values() starting...%s", person_id)
                value_row={}
                value_row['id'] = personObj.convert_person_id_to_study(person_id)
                #if mapping.has_date: # not possible when table is dual!!
                value_row['from_table'] =  mapping['from_table']
                value_row['from_column'] =  mapping['from_column']
                value_row['value'] =  mapping['from_column']
                value_rows.append(value_row)
            except Exception as  e:
                logger.error("migrate select_values() " + str(person_id) + " mapping: " + str(mapping))
                logger.error("migrate select_values() person:" + str(personObj))
                logger.error("migrate select_values() value_row:" + str(value_row))
                traceback.print_tb(e.__traceback__)
                logger.error("exception is:", e)
                raise e
        logger.info("migrate select_values() ...finishing dual")
        return(value_rows)
    else:
        logger.debug("ELSE")
        date_column_name = personObj.get_date_column_for_table(mapping['from_table'])
        id_column_name = personObj.get_id_field_name();
        logger.debug("select_values() starting.2. {} {} ...".format(date_column_name, id_column_name))
        if (not re.match('\w+."', mapping['from_table'], 0)):
            from_table_quoted =re.sub('\.', '."', mapping['from_table'], 1) + '"'
            logger.debug("RENAMING {} to {}".format(mapping['from_table'], from_table_quoted))
        else:
            from_table_quoted = mapping['from_table']
            logger.debug("NOT RENAMING {} ".format(mapping['from_table']))
        #if mapping.from_where_clause == None:
        if 'from_where_clause' not in mapping or mapping['from_where_clause'] == None:
            stmt = "SELECT " + id_column_name + " as id, "
            if 'has_date' in mapping and mapping['has_date']:
                stmt += date_column_name + " as date_value, "
            stmt += "'" + mapping['from_column'] + "' as from_column, " 
            stmt += "'" + from_table_quoted + "' as from_table, " 
            stmt += "\"" + mapping['from_column'] + "\" as value " 
            stmt += "  FROM "    + from_table_quoted  
            if 'has_date' in mapping and mapping['has_date']:
                stmt += " ORDER BY id, date_value "
            else:
                stmt += " ORDER BY id NULLS LAST"
        else:
            stmt = "SELECT " + id_column_name + " as id, "
            if 'has_date' in mapping and mapping['has_date']:
                stmt += date_column_name + " as date_value, "
            stmt += "'" + mapping['from_column'] + "' as from_column, " 
            stmt += "'" + from_table_quoted + "' as from_table, " 
            stmt += "\"" + mapping['from_column'] + "\" as value " 
            stmt += "  FROM "    + from_table_quoted  
            stmt += "  WHERE "    + mapping['from_where_column'] + " = '" + str(mapping['from_where_clause']) + "'"
            if 'has_date' in mapping and mapping['has_date']:
                stmt += " ORDER BY id, date_value "
            else:
                stmt += " ORDER BY id NULLS LAST"
        try:
            logger.info("QUERY: %s",stmt)
            logger.info("   QUERY: %s date_column_name", date_column_name)
            value_cursor.execute(stmt)
            value_rows = value_cursor.fetchall()
            if 'has_date' not in mapping or not mapping['has_date']:
                logger.debug("migrate_by_mappings() falling back to NULL date %s", mapping)
                for value_row in value_rows:
                    value_row['date_value'] = NULL_DATE
        except Exception as  e:
            logger.error("EXCEPTION:",e)
            logger.error(mapping, stmt)
            raise e

        logger.info("exiting")
        return(value_rows)

def migrate_by_mappings(con, mappings, observation_number_start, personObj, person_ids):
    """ Migrates values from a study's tables into OHDSI/OMOP. It does this for
        every subject/person in the study and is driven by the id's in the study's
        tables. It doesn't need the list of person_ids like when events_mapping is run.

        con - db connection
        mappings - list of StudyToOhdsiMapping objects
        observation_number_start - noise?
        personObj - Person class object used for study-specific code
        person_ids - 
    """
    logger.info("migrate_by_mappings() start  %d", len(mappings))
    observation_number=observation_number_start
    value_cursor = con.cursor(cursor_factory=RealDictCursor)
    id_column_name = personObj.get_id_field_name();
    for mapping in mappings:
        try:
            logger.info("MAPPINGXX1 {} ".format(mapping))
            value_rows=[]
            value_rows=select_values(mapping, personObj, person_ids, value_cursor)
    
            arguments = StudyMappingArguments.objects.filter(
                study_id=mapping.study_id,
                from_table=mapping.from_table, 
                from_column=mapping.from_column,
                function_name=mapping.function_name).values()
 
            # INSERT values into ohdsi
            try:
                concept_id = Concept.objects.get(vocabulary_id=mapping.vocabulary_id, concept_code=mapping.concept_code).concept_id
            except Exception as x:
                logger.error("concept lookup failed %s %s", mapping.vocabulary_id, mapping.concept_code)
                logger.error("....exception: %s", x)
                raise x
            if concept_id == None:
                logger.error("migrate_by_mappings(): null concept_id from %s", mapping)
                raise Exception("null concept id in migrate_by_mappgings() for vocabulary \"{mapping.vocabulary_id}\" concept \"{mapping.concept_code}\" ")
            else:
                for value_row in value_rows:
                    if value_row['value'] == None :
                        logger.warn("migrate_by_mappings(): had a null value in the from_column %s %s   %s %s", mapping.from_column,  
                            value_row['value'], personObj, value_row)
                    try:
                        value = None
                        if (value_row and (value_row['value'] is not None)):
                            value = _map_column_value(mapping, value_row['value'], arguments, con)  
                    except Exception as e:
                        logger.error("Error applying function %s %s %s", mapping, value_row, arguments)
                        logger.error("Error applying function exception:%s", e)
                        logger.exception(e)
                        raise e
                    if value == None :
                        logger.error("migrate_by_mappings(): mapping produced null value (or there was an error applying function) from %s, %s", 
                            value_row['value'], mapping)
                    else:
                        ohdsi_id_value =     personObj.convert_person_id_to_ohdsi(value_row['id'])
                        if 'date_value' in value_row:
                            date_value = value_row['date_value']
                        else:
                            date_value = NULL_DATE;
                        try: 
                            insert_ohdsi(con, mapping.to_table, mapping.to_column, observation_number, ohdsi_id_value, date_value, concept_id, value)
                        except psycopg2.DataError as e:
                            logger.warning("bogus data:%s, for person:%s and concept:%s", value, ohdsi_id_value, concept_id)
                            logger.error("exception: %s", e)
                            raise e;
                        observation_number += 1
        except Exception as e:
            logger.exception(e)
            traceback.print_tb(e.__traceback__)
            raise e

    value_cursor.close()
    return observation_number

def how_many_nonnull_observations(con):
    try:
        cur = con.cursor()
        cur.execute("select count(*) from observation where (value_as_string is not null or value_as_number is not null or  value_as_concept_id is not null)")
        rows=cur.fetchall();
        logger.info("%s non-null rows in observation table", str(rows[0]))
        cur.close()
    except Exception as e:
        logger.error("migrate.how_many_nonnull_observations, error %s", e)
        raise e

def how_many_observations(con):
    try:
        cur = con.cursor()
        cur.execute("select count(*) from observation ")
        rows=cur.fetchall();
        logger.info("%srows in observation table", str(rows[0]))
        cur.close()
    except Exception as e:
        logger.error("migrate.how_many_observations, error %s", e)
        raise e


def migrate(con, study_id, observation_number_start):
    logger.info("migrate.migrate() %d, %d", study_id, observation_number_start)
    study = Study.objects.get(study_id=study_id)
    logger.info("migrate.migrate() got study: %s", study)
    personObj = BasePerson.factory(study)  
    logger.info("migrate.migrate() got person %s", personObj)
    logger.info("POPULATING  PERSON study:%d personObj:%s", study_id, personObj)
    personObj.populate_person(con) 
    person_ids = personObj.get_study_person_ids(con)

    logger.info("MIGRATING EVENTS study:%d personObj:%s", study_id, personObj)
    events_mapping.populate(con, person_ids, study) 

    logger.info("done, MIGRATING EVENTS, getting global_mappings")
    global_mappings = StudyToOhdsiMapping.objects.filter(study_id=study_id) 
    logger.info("MIGRATING study %d with %d mappings ", study_id, len(global_mappings))
    max_observation = migrate_by_mappings(con, global_mappings, observation_number_start, personObj, person_ids)
    con.commit()
    return max_observation


def _execute(con, stmt, args):
    cur = con.cursor()
    cur.execute(stmt, args)
    cur.close()

def _truncate_study(con, name) :
    try:
        (study_id, observation_range_start, observation_range_end, person_id_start, person_id_end) = get_study_details(con, name)
        logger.warn("TRUNCATING %s %s %s %s %s %s",name, study_id, observation_range_start, observation_range_end, person_id_start, person_id_end)
        _execute(con, "delete from observation where person_id >= %s and person_id < %s", (person_id_start, person_id_end))
        _execute(con, "delete from measurement where person_id >= %s and person_id < %s", (person_id_start, person_id_end))
        _execute(con, "delete from visit_occurrence where person_id >= %s and person_id < %s", (person_id_start, person_id_end))
        _execute(con, "delete from procedure_occurrence where person_id >= %s and person_id < %s", (person_id_start, person_id_end))
        _execute(con, "delete from death where person_id >= %s and person_id < %s", (person_id_start, person_id_end))
        _execute(con, "delete from person where person_id >= %s and person_id < %s", (person_id_start, person_id_end))
    
        cur = con.cursor()
        stmt = "SELECT count(*) from person where person_id >= %s and person_id < %s";
        cur.execute(stmt, (person_id_start, person_id_end))
        rows = cur.fetchall()
        cur.close()
        if (len(rows) > 0):
            logger.info("STUDY %s down to %d rows", name, rows[0][0])
        else:
            logger.error("STUDY %s doesn't seem to have truncated properly",name)
    except Exception as e:
        logger.error("migrate.how_many_observations, error %s", e)
        raise e


# throws on error
def main(db_name, user_name, study_name) :
    try:
        con = psycopg2.connect(database=db_name, user=user_name) 
        con.autocommit=True;
    
        _truncate_study(con, study_name)
        (study_id, observation_range_start, observation_range_end, _, _) = get_study_details(con, study_name)
        logger.info("MIGRATING %s, %s at observation number %s", study_id, study_name, observation_range_start)
        max_observation_number =  migrate(con, study_id, observation_range_start)
        if (max_observation_number > observation_range_end):
            logger.error("migrate error %s %s %s %s",
                 max_observation_number, observation_range_end, study_id, study_name)
            raise ValueError("too many observations from study",
                 max_observation_number, observation_range_end, study_id, study_name)
        else:
            logger.debug("migrate success %s %s %s %s",
                 max_observation_number, observation_range_end, study_id, study_name)
    
        how_many_observations(con)
        how_many_nonnull_observations(con)
        logger.warning("MIGRATE complete")
    except Exception as e:
        con.close()
        logger.exception(e)
        raise e

    try:
        update_stmt = 'UPDATE study set migrated=\'t\' where study_name=%s'
        update_cur = con.cursor()
        update_cur.execute(update_stmt, (study_name,) )
        con.close()
    except Exception as  e:
        logger.error("unable to mark %s as migrated: %s, %s",  study_name, e, update_stmt)
        raise e

