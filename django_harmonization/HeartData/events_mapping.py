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
 events_mapping.py
 Python Version: 3.6.3

 Queries the study by the events_mapping table and populates OHDSI tables Death, visit_occurrence and procedure_occurrence.

 This is research code for demonstration purposes only.

 croeder 8/2017 chris.roeder@ucdenver.edu
'''

import logging
from HeartData import migrate
#import datetime
#import sys
#import re
import psycopg2
from psycopg2.extras import RealDictCursor
from HeartData.person import BasePerson

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NULL_PLACEHOLDER='no_column'

def _read_event_mappings(con, study_id):
    event_mappings={}
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute( ("SELECT study_id, from_table, from_column, to_table, value_vocabulary_id, value_concept_code, addl_column, addl_value, from_date_column, where_clause"
                  " FROM events_mapping "
                  " WHERE study_id = %s"), (study_id,) )
    rows = cur.fetchall()
    cur.close()
    return rows

def populate(con, person_id_list, study_id):
    """ populate the ohdsi person table.
        Be wary of the fact that the list of person_ids is a list of ohdsi_ids,
        and that when you query study tables those ids need converted.
    """
    personObj = BasePerson.factory(study_id)
    cur = con.cursor()
    event_mappings = _read_event_mappings(con, study_id)
    procedure_id=0
    visit_id=0
    for row in event_mappings:
        for person_id in person_id_list:
            query=""

            # QUERY FOR THE VALUES,  BEST SPECIFIC? TODO
            from_table_name=row['from_table']
            id_col = personObj.get_id_field_name()
            prefix = from_table_name.split('_')[0]
            if (row['from_column'] != NULL_PLACEHOLDER):
                # a value and a date, like the Death table
                if (row['where_clause'] != NULL_PLACEHOLDER) :
                    query = ("select {0}, {1} from {2} where " + id_col + " = %s and ( {3} )").format(row['from_date_column'], row['from_column'], row['from_table'], row['where_clause'])
                    logger.debug("QUERY1:%s  %s", query, person_id)
                    cur.execute(query, (personObj.convert_person_id_to_study(person_id),))
                else:
                    query = ("select {0}, {1} from {2} where " + id_col + " = %s").format(row['from_date_column'], row['from_column'], row['from_table'])
                    logger.debug("QUERY2: %s, %s", query, row)
                    cur.execute(query, (personObj.convert_person_id_to_study(person_id),))
            else:
                # just a date, like the Occurrence tables:
                if (row['where_clause'] != NULL_PLACEHOLDER) :
                    query = ("select {0} from {1} where " + id_col + " = %s and ( {2} )").format(row['from_date_column'], row['from_table'], row['where_clause'])
                    logger.debug("QUERY3: %s   %s", query, row)
                    cur.execute(query, (personObj.convert_person_id_to_study(person_id),))
                else:
                    query = ("select {0} from {1} where " + id_col + " = %s").format(row['from_date_column'], row['from_table'])
                    logger.debug("QUERY4:  %s  %s", query, row)
                    cur.execute(query, (personObj.convert_person_id_to_study(person_id),))
            value_rows = cur.fetchall()
            logger.debug("events.populate() from:%s to:%s rows:%d", from_table_name, row['to_table'], len(value_rows))

            # LOOKUP the id (vocab, concept) from the mappings row
            concept_id = migrate.get_concept_id(con, row['value_vocabulary_id'], row['value_concept_code'])

            # INSERT
            if (len(value_rows) == 0):
                logger.warn("no rows back from %s person:%s, with %s", query, person_id, row)
            elif (concept_id == None) :
                logger.error("None concept from get_concept_id() %s, %s", row['value_vocabulary_id'], row['value_concept_code'])
            else:
                for value_row in value_rows:
                    if value_row[0] != None :
                        logger.debug("VALUE ROWS pid:%s  query:%s  value:%s  num-rows:%d", person_id, query,  value_row, len(value_rows))
                        to_table_name=row['to_table']
                        # sometimes this is a date, sometimes a string. Use string, the lowest-common denominator, works for all sources
                        the_date_value=''
                        try:
                            date_time_string = str(value_row[0])
                            (year, month, day)  = date_time_string.split(' ')[0].split('-')
                            the_date_value = "{0}/{1}/{2}".format(month, day, year)
                        except:
                            logger.error("populate raised on {}".format(date_time_string))
                            the_date_value = date_time_string

                        # INSERT DEATH
                        if to_table_name == 'Death':
                            statement = "insert into death (person_id, death_date, death_datetime, death_type_concept_id, cause_concept_id)" \
                                + " values ( %s,  %s, %s,  %s, %s)"
                            logger.debug("death: %s, %s, %s, %s, %s %s %s %s); ",
                                statement, person_id, the_date_value, row['addl_value'], concept_id,
                                row['value_vocabulary_id'], row['value_concept_code'], value_row[0] )

                            cur.execute(statement, (person_id, the_date_value, the_date_value, row['addl_value'], concept_id))

                        # INSERT VISIT OCCURRENCE
                        elif to_table_name == 'visit_occurrence':
                            statement = ("insert into visit_occurrence "
                                        "(visit_occurrence_id, person_id, visit_concept_id, visit_start_date, "
                                        " visit_start_datetime, visit_end_date,  visit_type_concept_id)"
                                        " values ( %s,  %s,  %s,  %s, %s, %s, %s)")
                            logger.debug("visit %s %s %s %s %s %s %s %s", statement, visit_id, person_id, concept_id, the_date_value,
                                row['addl_value'], row['value_vocabulary_id'], row['value_concept_code'])
                            cur.execute(statement, (visit_id, person_id, concept_id,  the_date_value, the_date_value, the_date_value, row['addl_value']))
                            visit_id += 1

                        # INSERT PROCEDURE  OCCURRENCE
                        elif to_table_name == 'procedure_occurrence':
                            statement = ("insert into procedure_occurrence"
                                        " (procedure_occurrence_id, person_id, procedure_concept_id, "
                                        "  procedure_date, procedure_datetime, procedure_type_concept_id)"\
                                        " values ( %s,  %s,  %s,  %s, %s, %s)")
                            logger.debug("proc: %s %s %s %s *%s* %s %s %s %s", statement, procedure_id, person_id, concept_id,
                                the_date_value, row['addl_value'], row['value_vocabulary_id'], row['value_concept_code'], value_row[0] )
                            cur.execute(statement, (procedure_id, person_id, concept_id, the_date_value, the_date_value, row['addl_value']))
                            procedure_id += 1
                        else:
                            logger.error("unknown table name %s in events.populate() %s", to_table_name, row)
                    else:
                        logger.warn("None value in  events_mapping.populate() with %s", value_row)
        value_rows=None

    cur.close()
    con.commit()



