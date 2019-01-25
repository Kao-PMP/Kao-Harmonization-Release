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
 consistency_categorization.py
 Python Version: 3.6.3

 post-migration, this script categorizes values in the source files so the results
 can be compared to result values derived out of ohdsi.

 This is research code for demonstration purposes only.

 croeder 2/2018 chris.roeder@ucdenver.edu
'''


import logging
import datetime
import collections
import importlib
import sys
import re
import argh
import psycopg2
from psycopg2.extras import RealDictCursor
import person
import observation

from migrate import read_mappings
from migrate import MAPPING_NOT_USED
from migrate import IDENTITY_MAPPING
from migrate import VALUE_AS_STRING
from migrate import VALUE_AS_NUMBER
from migrate import VALUE_AS_CONCEPT_ID

from person import  BasePerson
from study import get_study_details

from consistency_stats import get_study_rows

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


##def _get_study_rows(study_id, patient_id, from_table, from_column, personObj, con):

def get_categorization_info(conn, extract_cfg_id, vocabulary_id, concept_code):
    stmt = ("SELECT m.*, p.* "
            "FROM categorization_function_metadata m, categorization_function_parameters p "
            "WHERE m.extract_study_id = p.extract_study_id "
            "and m.function_name = p.function_name "
            "and m.long_name = p.long_name   "
            "and m.rule_id = p.rule_id "
            "and m.extract_study_id = %s "
            "and m.from_vocabulary_id = %s "
            "and m.from_concept_code = %s "
            "order by rank; ")
    cur = conn.cursor()
    cur.execute(stmt, (extract_cfg_id, vocabulary_id, concept_code))
    study_rows = cur.fetchall()
    return study_rows

def get_study_count_in_range(conn, extract_study_id,  from_table,  from_column,  personObj, bottom, top):
    visit_date_column = personObj.get_date_column_for_table(from_table);
    cur = conn.cursor()
    id_field_name = personObj.get_id_field_name();
    stmt = "SELECT count(*) FROM " + from_table + " WHERE " + from_column + " is not null and " + from_column + " > %s and " + from_column + " <= %s"
    cur.execute(stmt, (bottom, top))
    study_rows = cur.fetchall()
    cur.close()
    return study_rows[0][0]

def get_study_total(conn, extract_study_id,  from_table,  from_column,  personObj):
    visit_date_column = personObj.get_date_column_for_table(from_table);
    cur = conn.cursor()
    id_field_name = personObj.get_id_field_name();
    stmt = "SELECT count(*) FROM " + from_table + " WHERE " + from_column + " is not null"
    cur.execute(stmt)
    study_rows = cur.fetchall()
    cur.close()
    return study_rows[0][0]

def get_concept_name(conn, vocab, concept):
    cur = conn.cursor()
    stmt = "SELECT concept_name FROM concept WHERE vocabulary_id = %s and concept_code = %s"
    cur.execute(stmt, (vocab, concept))
    study_rows = cur.fetchall()
    cur.close()
    return study_rows[0][0]

# (study | ohdsi) -> to_column -> value -> count

def build_comparison(conn, extract_study_id, personObj, mappings):
    """ builds a map of frequency distributions """
    # cur.execute(("SELECT extract_study_id, from_table, from_column, function_name, vocabulary_id, concept_code, to_table, to_column, from_where_clause, from_where_column "
    #{'study_id': 5, 'from_table': 'paradigm.test', 'from_column': 'trtnrand', 'function_name': 'topcat_yes_no_to_concept', 
    #'vocabulary_id': 'UCD.Kao', 'concept_code': 'UCD-Kao-19', 'to_table': 'observation', 'to_column': 'value_as_concept_id', 'from_where_clause': None, 'from_where_column': None, 'has_date': False}

    for mapping in mappings:
        ##(paradigm.test, sgpt_1) (LOINC, 1920-8) value_as_number
        concept_name = get_concept_name(conn,  mapping['vocabulary_id'], mapping['concept_code'])
        function_rows = get_categorization_info(conn, 5001, mapping['vocabulary_id'], mapping['concept_code'])
        if (len(function_rows) > 0):
            show_main=False
            bottom=0.0
            top=sys.maxsize
            for f_row in function_rows:
                total = get_study_total(conn, extract_study_id, mapping['from_table'], mapping['from_column'], personObj)
                if (show_main == False ):
                    print("{} ({}, {}) ({}, {}) {} \"{}\"".format(f_row[8], mapping['from_table'], mapping['from_column'], 
                        mapping['vocabulary_id'], mapping['concept_code'], mapping['to_column'], 
                        concept_name))
                    show_main = True

                if (f_row[1] == 'ranges_to_rank_asc'):
                    # ASCENDING
                    if (f_row[13] is not None) :
                        top=f_row[13]
                    else:
                        top = sys.maxsize
                    count = get_study_count_in_range(conn, extract_study_id, mapping['from_table'], mapping['from_column'], personObj, bottom, top)
                    print("    ascending {}    {}-{}:{:4d} {:4.2f}%".format(f_row[14], bottom, top, count, count / total * 100))
                    bottom=top

                elif (f_row[1] == 'ranges_to_rank_desc'):
                    # DESCENDING
                    if (f_row[13] is not None) :
                        bottom=f_row[13]
                    else :
                        bottom=0
                    count = get_study_count_in_range(conn, extract_study_id, mapping['from_table'], mapping['from_column'], personObj, bottom, top)
                    print("   descending {}    {}-{}:{:4d} {:4.2f}%".format(f_row[14], bottom, top, count, count / total * 100))
                    top=bottom
                else:
                    print("    {}".format(f_row[1]))

def main(db_name, user_name, study_name, extract_study_id) :
    conn = psycopg2.connect(database=db_name, user=user_name) 
    conn.autocommit=True;

    (study_id, observation_range_start, observation_range_end, _, _) = get_study_details(conn, study_name)
    personObj = BasePerson.factory(study_id)  
    mappings = read_mappings(conn, study_id)
    comparison_data = build_comparison(conn, study_id, personObj, mappings)
    conn.close()

if __name__ == '__main__':
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)
