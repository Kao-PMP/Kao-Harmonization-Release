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
 report.py <db> <user>
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


def extract_calculation_arguments(con, study_id, to_vocabulary, to_concept_code, function_name):
    ''' fetch arguments to go with a calculation rule'''
    log = sys.stdout.write
    stmt = ("SELECT argument_name, value_field, vocabulary_id, concept_code, from_table "
            "FROM ohdsi_calculation_argument "
            "WHERE study_id = %s and to_concept_code = %s "
            "AND to_vocabulary_id = %s and function_name = %s")
    #print stmt, (study_id, to_vocabulary, to_concept_code, function_name)
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute(stmt, (study_id, to_concept_code, to_vocabulary, function_name))
    rows = cur.fetchall()
    for row in rows:
        log("   {}:{}, {}:{}  \"{}\"\n".format(row['vocabulary_id'],
                                           row['concept_code'],
                                           row['from_table'],
                                           row['value_field'],
                                           row['argument_name']))
    cur.close()
    sys.stdout.flush()

## TODO ohdsi_calculated_table

def report_calculated_concepts(con, study_id):
    '''  join the configuration of mapping together and produce/print a report '''
    log = sys.stdout.write
    stmt = ("SELECT ocf.function_name as fn, "
            "ocf.to_vocabulary_id as vocab, "
            "ocf.to_concept_code as concept, "
            "ocf.function_order as f_order "
            "FROM ohdsi_calculation_function ocf  "
            "WHERE ocf.study_id = %s "
            "ORDER BY ocf.to_concept_code, ocf.function_order ")
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute(stmt, (study_id,))
    rows = cur.fetchall()
    for row in rows:
        log(row['fn'] + " " + row['vocab'] + ":" + row['concept'] + " " + str(row['f_order']) + "\n")
        extract_calculation_arguments(con, study_id, row['vocab'], row['concept'], row['fn'])
        log("\n")
    cur.close()
    sys.stdout.flush()



def extract_function_parameters(con, function_name, long_name, rule_id):
    '''  fetch the parameters to go with an extraction function '''
    log = sys.stdout.write
    stmt = ("SELECT value_limit, from_string, from_concept_id, rank "
            "FROM categorization_function_parameters "
            "WHERE  function_name = %s "
            "AND long_name = %s "
            "AND rule_id = %s "
            "ORDER BY rank")
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute(stmt, (function_name, long_name, rule_id))
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

def report_mapped_concepts(con, study_id):
    ''' report and print the configuration 
        joins on categorization_function_metadata so it only shows 
        concepts used by direct extraction/categorization
    '''
    log = sys.stdout.write
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT m.study_id, m.from_table as m_from_table, "
            "m.from_column as m_from_column, "
            "m.function_name as m_function_name, "
            "m.vocabulary_id as vocab, "
            "m.concept_code as concept, "
            "m.to_table as m_to_table, "
            "m.to_column as m_to_column, "
            "c.from_table as c_from_table, "
            "c.function_name as c_function_name, "
            "c.long_name as c_long_name, c.rule_id "
            "FROM study_to_ohdsi_mapping m, categorization_function_metadata c "
            "WHERE m.study_id = %s "
            "AND m.function_name is not null "
            "AND m.vocabulary_id = c.from_vocabulary_id "
            "AND m.concept_code = c.from_concept_code "
            "ORDER BY m.study_id, c.long_name;")
    cur.execute(stmt, (study_id,))
    rows = cur.fetchall()
    for row in rows:
        (_, name) = get_concept_id_and_name(con, row['vocab'], row['concept'])
        log("\n\nFROM: {:26} \n"
            .format(row['m_from_table'] + ":" + row['m_from_column']))
        log("FUNC: {:28} \n"
            .format(row['m_function_name'] + "()"))
        log("  TO: {} {} {}\n".format(
                    row['vocab'] + ":" +  row['concept'], 
                    "\"" + name + "\"",
                    row['m_to_table'] + ":" +  row['m_to_column']))
        log("EXTR: {} \n".format(row['c_long_name']))
        extract_function_parameters(con, row['c_function_name'], row['c_long_name'], row['rule_id'])
    cur.close()
    sys.stdout.flush()

def report_unmapped_concepts(con, study_id):
    ''' report and print the configuration 
        doesn't have the jion as above, lists concepts that might be used
        as input to further calculation
    '''
    log = sys.stdout.write
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT m.study_id, m.from_table as m_from_table, "
            "m.from_column as m_from_column, "
            "m.function_name as m_function_name, "
            "m.vocabulary_id as vocab, "
            "m.concept_code as concept, "
            "m.to_table as m_to_table, "
            "m.to_column as m_to_column, "
            "o.function_name as function_name "
            "FROM study_to_ohdsi_mapping m "
            "    JOIN ohdsi_calculation_argument o "
            "      ON m.vocabulary_id = o.vocabulary_id "
            "     AND o.concept_code = m.concept_code "
            "     AND o.study_id = m.study_id "
            "WHERE m.study_id = %s "
            "  AND m.function_name is not null "
            "ORDER BY m.study_id;")
    cur.execute(stmt, (study_id,))
    rows = cur.fetchall()
    for row in rows:
        (concept_id, name) = get_concept_id_and_name(con, row['vocab'], row['concept'])
        if concept_id != None and name != None:
            log("\nFROM: {:26} \n".format(
                row['m_from_table'] + ":" + row['m_from_column']))
            log("FUNC: {:28} \n".format(
                row['m_function_name'] + "()"))
            log("  TO: {} {} {}\n".format(
                    row['vocab'] + ":" +  row['concept'],
                    "\"" + name + "\"",
                    row['m_to_table'] +  ":" +  row['m_to_column']))
            log("INTO: {}()\n".format(row['function_name']))
    cur.close()
    sys.stdout.flush()

def report_calculated_extraction(con, study_id, extract_study_id):
    ''' Shows categorization for results of calculations.
        This is for concepts that don't come directly from input tables, rather
        ones that are calculated.
    '''
    log = sys.stdout.write
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT "
            "c.from_vocabulary_id, "
            "c.from_concept_code, "
            "c.from_table, "
            "c.function_name, "
            "c.long_name,  "
            "c.rule_id "
            "FROM categorization_function_metadata c "
            " LEFT JOIN study_to_ohdsi_mapping m "
            "        ON m.vocabulary_id = c.from_vocabulary_id "
            "       AND m.concept_code = c.from_concept_code "
            "WHERE m.study_id = %s "
            " AND c.extract_study_id = %s "
            "AND m.function_name is  null "
            "ORDER BY m.study_id, c.long_name;")

    cur.execute(stmt, (extract_study_id, study_id,))
    rows = cur.fetchall()
    for row in rows:
        (_, name) = get_concept_id_and_name(con, row['from_vocabulary_id'], row['from_concept_code'])
        log("{}()  {}:{} \"{}\" -->{} \n".format(row['function_name'], row['from_vocabulary_id'], row['from_concept_code'], name, row['long_name']))
        extract_function_parameters(con, row['function_name'], row['long_name'], row['rule_id'])
        log("\n\n")
    cur.close()
    sys.stdout.flush()


def report_events_mapping(con, study_id):
    log = sys.stdout.write
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT from_table, from_column, value_vocabulary_id, value_concept_code, to_table, to_column, from_date_column, where_clause, comment "
            "  FROM events_mapping "
            " WHERE study_id = %s")
    cur.execute(stmt, (study_id,))
    rows = cur.fetchall()
    for row in rows:
        (_, name) = get_concept_id_and_name(con, row['value_vocabulary_id'], row['value_concept_code'])
        log("{}:{} --> {}:{} {}:{} \"{}\" where {}  {}\n".format(
            row['from_table'], row['from_column'],
            row['to_table'], row['to_column'],
            row['value_vocabulary_id'], row['value_concept_code'], name,
            row['where_clause'],
            row['from_date_column'], 
        ))
        comment = row['comment']
        if comment != None:
            log("    {}\n".format(comment))
        log("\n")
    cur.close()
    sys.stdout.flush()


def report_wide_extraction(con, extract_study_id):
    log = sys.stdout.write
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT from_table, from_column, from_vocabulary_id, from_concept_code, function_name, long_name "
            "  FROM categorization_function_table "
            " WHERE extract_study_id = %s")
    cur.execute(stmt, (extract_study_id,))
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


def main(db_name, user_name, study_name, extract_study_id) :
    logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name

    conn = psycopg2.connect(database=db_name, user=user_name)
    conn.autocommit = True
    (study_id, observation_range_start, observation_range_end, _, _) = get_study_details(conn, study_name)
    
    print("=============", study_id, "=================")
    print("\n-- mapped and extracted concepts ------------\n")
    report_mapped_concepts(conn, study_id)
    print("\n-- unextracted concepts ------------\n")
    report_unmapped_concepts(conn, study_id)
    print("\n-- calculated ------------\n")
    report_calculated_concepts(conn, study_id) 

    print("\n -- events mapping -----------\n")
    report_events_mapping(conn, study_id)
    
    print("\n-- calculated extraction ----------\n")
    report_calculated_extraction(conn, study_id, extract_study_id) 
        
    print("\n-- wide extraction ----------\n")
    report_wide_extraction(conn, extract_study_id) 
    conn.close()

if __name__ == '__main__':
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)
    
