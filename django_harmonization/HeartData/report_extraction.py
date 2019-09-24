#!/usr/bin/env python3
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
 report_extraction.py <db> <user> <study_id> <extraction_id>
    db - is the name of the database within postgresql
    user - is the user with permissions in posgresql
    study_id - is the study id we're importing to OHDSI, see the study table
    extraction_id - is the extraction configuration used to query the categorization_* tables

 Python Version: 3.6.3

 a report that shows the mapping from a study to ohdsi and on to an extraction matrix.

 TODO: I believe it doesn't show the path between migration and concepts used as input to
 calculation functions. I think that's because it works backwards from the
 categorization/extraction end.
 It doesn't read through the calcuations to include their input.s


 This is research code for demonstration purposes only.

 croeder 6/2017 chris.roeder@ucdenver.edu
'''

import logging
import sys
import psycopg2
import argh
from psycopg2.extras import RealDictCursor
from study import get_study_details

log = sys.stdout.write

def get_concept_id_and_name(con, vocabulary, concept_code):
    ''' given a vocabulary name and concept code, return the concept_id within OHDSI CDM'''
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT concept_id, concept_name "
            "FROM concept "
            "WHERE concept_code = %s and vocabulary_id = %s")
    cur.execute(stmt, (concept_code, vocabulary))
    rows = cur.fetchall()
    cur.close()
    if rows:
        return (rows[0]['concept_id'], rows[0]['concept_name'])
    # else:
    return (None, None)


def extract_function_parameters(con, function_name, long_name, rule_id, extraction_id):
    '''  fetch the parameters to go with an extraction function '''
    stmt = ("SELECT value_limit, from_string, from_concept_id, rank "
            "FROM categorization_function_parameters "
            "WHERE  function_name = %s "
            "AND long_name = %s "
            "AND rule_id = %s "
            "AND extract_study_id = %s " 
            "ORDER BY rank")
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute(stmt, (function_name, long_name, rule_id, extraction_id))
    rows = cur.fetchall()
    cur.close()

    prefix = ""
    if rows:
        log("   CAT: " + function_name + "(")
    row_count = 0
    for row in rows:
        row_count += 1
        thing = ""
        if prefix == "" and function_name[-3:] == 'asc':
            prefix = "up to"
        elif prefix == "" and function_name[-4:] == 'desc':
            prefix = "down to"
        if row['value_limit'] != None:
            thing = row['value_limit']
        elif row['from_string'] != None:
            thing = row['from_string']
        elif row['from_concept_id'] != None:
            thing = row['from_concept_id']
        else:
            prefix = ""
            thing = 'remainder'
        log("{}:{} ".format(prefix, thing))
        log("INTO: {}".format(row['rank']))
        if row_count < len(rows):
            log(", ")
    if rows:
        log(")")
    else:
        log("   CAT: (no categorization, value passed on as-is)")
    #    log("      missing? {} {} {}".format(function_name, long_name, rule_id))

    sys.stdout.flush()

def report_narrow_extraction(con, study_id, extraction_id):
    ''' Shows categorization for results of calculations.
        This is for concepts that don't come directly from input tables, rather
        ones that are calculated.
    '''
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT "
            "c.from_vocabulary_id, "
            "c.from_concept_code, "
            "c.from_table, "
            "c.function_name, "
            "c.long_name,  "
            "c.short_name,  "
            "c.rule_id "
            "FROM categorization_function_metadata c "
            "WHERE c.extract_study_id = %s "
            "ORDER BY c.extract_study_id;")

    #cur.execute(stmt, (study_id, extraction_id))
    cur.execute(stmt, (extraction_id,))
    rows = cur.fetchall()
    for row in rows:
        (_, name) = get_concept_id_and_name(con, row['from_vocabulary_id'], row['from_concept_code'])
        log("{}()  {}:{} \"{}\" --> \"{}\" / \"{}\" \n".format(row['function_name'], row['from_vocabulary_id'], row['from_concept_code'], name, row['long_name'], row['short_name']))
        extract_function_parameters(con, row['function_name'], row['long_name'], row['rule_id'], extraction_id)
        log("\n\n")
    cur.close()
    sys.stdout.flush()


def report_wide_extraction(con, extraction_id):
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT from_table, from_column, from_vocabulary_id, from_concept_code, function_name, long_name "
            "  FROM categorization_function_table "
            " WHERE extract_study_id = %s") 
    cur.execute(stmt, (extraction_id,))
    rows = cur.fetchall()
    for row in rows:
        (_, name) = get_concept_id_and_name(con, row['from_vocabulary_id'], row['from_concept_code'])
        log("\"{}\" <-- {}()  {}:{} where: {}:{} \"{}\" \n".format(   
            row['long_name'], 
            row['function_name'],
            row['from_table'], row['from_column'],
            row['from_vocabulary_id'], row['from_concept_code'], name
            ))
        log("\n")
    cur.close()
    sys.stdout.flush()


def main(db_name, user_name, study_name, extraction_id) :
    logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name

    conn = psycopg2.connect(database=db_name, user=user_name)
    conn.autocommit = True
    (study_id, observation_range_start, observation_range_end, _, _) = get_study_details(conn, study_name)
    
    print("\n-- calculated extraction ----------\n")
    report_narrow_extraction(conn, study_id, extraction_id) 
        
    print("\n-- wide extraction ----------\n")
    report_wide_extraction(conn, extraction_id) 
    conn.close()



if __name__ == '__main__':
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)
    
