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
 columns.py (optional)
 Python Version: 3.6.3

 This script reads the (configured) database's metadata for table names.
 For each table and column, it builds entries in study_concept_type for the
 columns and in study_concept_value for the values. Though meant to pick up
 tables related to a clinical study (BEST at first), it picks up a few others.
 After creation with this script, this data has been annotated with descriptions
 from PDF documents. The data is then used as the starting point for developing
 a mapping from the study into OHDSI.

 This is research code for demonstration purposes only.

 croeder 6/2017 chris.roeder@ucdenver.edu
'''

import sys
import psycopg2
import logging

def convert_to_string(value):
    ''' convert to string '''
    retval = ""
    if type(value) == int or type(value) == long:
        retval = str(value)
    else:
        # look out for values that have single quotes in them (')
        retval = "'" + str(value).replace("'", "''") + "'"
    return retval

def insert_new_concept_type(study_id, name, filename):
    ''' insert  concept type into  table'''
    insert_stmt = "INSERT INTO study_concept_type (study_id, name, filename) VALUES ( %s, %s, %s)"
    insert_cur = CONNECTION.cursor()
    insert_cur.execute(insert_stmt, (study_id, name, filename))
    insert_cur.close()


# (study_id, study_concept_type_id, study_concept_value_id, name, desc )
def insert_new_concept_value(study_id, table, concept_value_name, concept_type_name):
    ''' insert new concept value '''
    insert_stmt = ("INSERT INTO study_concept_value (study_id, study_concept_type_id, name)"
                   " values (%s,"
                   " (SELECT study_concept_type_id FROM study_concept_type WHERE name = %s and filename = %s), "
                   " %s)")
    insert_cur = CONNECTION.cursor()
    insert_cur.execute(insert_stmt, (study_id, concept_type_name, table, concept_value_name))
    insert_cur.close()

def column_histogram(study_id, table, column, cursor):
    ''' build a frequency distribution of values in a column '''
    if column != "group" and column != "id" and column != "index" and column != "vdate" and table != 'concept_type' and table != 'concept_value':
        stmt = "SELECT distinct %s FROM %s"
        cursor.execute(stmt, (column, table))
        values = cursor.fetchall()
        cursor.close()
        for value in values:
            if value != None and value[0] != None:

                # build value table
                ###insert_new_concept_value(study_id, value[0], table + ":" + column)
                insert_new_concept_value(study_id, table, value[0], column)
                count_statement = "SELECT count(*) FROM %s WHERE %s = %s"
                count_cur = CONNECTION.cursor()
                count_cur.execute(count_statement, table, column, value[0])
                #value_count = count_cur.fetchone()
                count_cur.close()
                #if (type(value[0]) == str):
                #    print "column_histogram:", table + ":" +  column,  "count:", value_count[0], "value:\"" + str(value[0]) + "\""
                #else:
                #    print "column_histogram:", table + ":" +  column,  "count:", value_count[0], "value:" + str(value[0])
            #else:
                #print "column_histogram:", table + ":" +  column,  "value:", None

if __name__ == '__main__':

    STUDY = 1 # for BEST
    DBNAME = sys.argv[1]
    USERNAME = sys.argv[2]
    CONNECTION = psycopg2.connect(database=DBNAME, user=USERNAME)
    logger = logging.getLogger(__name__)
    
    # BEST tables (BEST specific hard-coded to avoid picking up other large tables in the db) TODO FIX
    TABLES = "('adju', 'ame', 'bestgenotype', 'br', 'clab1', 'clab2', 'cotx1', 'cotx2', 'cvh1', 'cvh2', 'cvs', 'diab', 'ecg', 'eos', 'hv', 'lab1', 'lab2', 'mi', 'miadju', 'mort1', 'mort2', 'muga', 'ne', 'pcsf', 'pe', 'permdc', 'phyga', 'pnelab', 'ptga', 'qol1', 'qol2', 'qol3', 'sct1', 'smed', 't', 'wd', 'xp', 'xray')"
    
    with CONNECTION:
        CUR = CONNECTION.cursor()
        ###sql="select table_name, column_name, data_type from  information_schema.columns where table_name in (select tablename from pg_catalog.pg_tables where schemaname = 'public' and tableowner='" + USERNAME + "');"
        SQL = "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_name in " + TABLES + ";"
        CUR.execute(SQL)
        ROWS = CUR.fetchall()
        CUR.close()

        CUR = CONNECTION.cursor()
        for in_row in ROWS:
            if in_row[0] != "csv/br": # FIX, what's up with that?
                insert_new_concept_type(str(STUDY), in_row[1], in_row[0])
                column_histogram(str(STUDY), in_row[0], in_row[1], CUR)
            CONNECTION.commit()
        CUR.close()
