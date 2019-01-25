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
 consistency_stats.py
 Python Version: 3.6.3

 After migration, this script  counts values in each column (logically in the case of a long or melted table) 
 for both migration and analysis matrix extraction.

 dates are driven by what is in Ohdsi.. TODO

 This is research code for demonstration purposes only.

 croeder 10/2017 chris.roeder@ucdenver.edu
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


logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

BEST_exceptions = ["best.ame", "best.clab1", "best.clab2", "best.lab1", "best.lab2"]
MAX_CONCEPTS_TO_LIST=10

def format_date_string_by_dataset(datetime_object, dataset_name): # TODO move to person, to be moved...
    #if (dataset_name == 'best.br' or dataset_name == 'best.pcsf'):
    if (dataset_name == 'best.pcsf'):
        # date string: 7/18/96 0:00
        date_string = str(datetime_object.month)  + "/" + str(datetime_object.day)  + "/" + str(datetime_object.year)[2:4]   + " 0:00"
        ##logger.info("br '%s'  %s   %s", date_string, str(datetime_object), str(datetime_object.year)[2:4])
        return date_string
    else:
        date_string = datetime_object.strftime("%Y-%m-%d") + " 00:00:00"
        return date_string

def _get_concept_name(column, con) :
    (study, vocab, concept) = column
    cur = con.cursor()
    stmt = "SELECT  concept_name from concept where vocabulary_id = %s and concept_code = %s"
    cur.execute(stmt, (vocab, concept))
    study_rows = cur.fetchall()
    return study_rows[0][0]

def get_study_rows(study_id, patient_id, from_table, from_column, personObj, con):
    visit_date_column = personObj.get_date_column_for_table(from_table);
    with  con.cursor() as cur:
        try:
            id_field_name = personObj.get_id_field_name();
            stmt = "SELECT " + from_column 
            if (from_table != 'dual'):
                stmt = stmt    + " FROM " + from_table
            if (study_id == 1) : # TODO BEST SPECIFIC
                if (from_table != 'dual'):
                    stmt += " WHERE id = %s and " + from_column + " is not null ORDER BY " + visit_date_column 
                    cur.execute(stmt, (patient_id,))
                else:
                    cur.execute(stmt)
            elif (study_id == 2): # TODO HF-ACTION SPECIFIC, no date column, id is called newid
                if (from_table != 'dual'):
                    stmt += " WHERE newid = %s and " + from_column + " is not null"
                    study_patient_id = personObj.convert_person_id_to_study(patient_id)
                    cur.execute(stmt, (study_patient_id,))
                else:
                    cur.execute(stmt)
            else:
                if (from_table != 'dual'):
                    stmt += " WHERE " + id_field_name + " = %s and " + from_column + " is not null"
                    study_patient_id = personObj.convert_person_id_to_study(patient_id)
                    cur.execute(stmt, (study_patient_id,))
                else:
                    cur.execute(stmt)
            study_rows = cur.fetchall()
        except Exception as e:
            logger.error("exception %s", e)
            logger.error("  query:%s study_id:%s id:%s from_table:%s from_column:%s", stmt, study_id, study_patient_id, from_table, from_column)
            raise e
    return study_rows


def get_ohdsi_rows(to_table, to_column, vocabulary_id, concept_code, patient_id, con):
    date_column = "o." + to_table + "_date"
    stmt = "SELECT " + to_column + ", " + date_column\
         + "  FROM " + to_table + " o " \
         +  "  JOIN concept c "\
         +  "    ON c.concept_id = o." + to_table + "_concept_id"\
         +  "   AND c.vocabulary_id = %s"\
         +  "   AND c.concept_code = %s"\
         +  " WHERE o.person_id = %s" \
         + " AND " + to_column + " is not null " \
         + " ORDER BY " + date_column
    cur = con.cursor()
    cur.execute(stmt,  (vocabulary_id, concept_code, patient_id))
    ohdsi_rows = cur.fetchall()
    cur.close()
    return ohdsi_rows


# (study | ohdsi) -> to_column -> value -> count

def build_comparison(con, patient_ids, study_id, personObj, mappings):
    """ builds a map of frequency distributions """
    # cur.execute(("SELECT study_id, from_table, from_column, function_name, vocabulary_id, concept_code, to_table, to_column, from_where_clause, from_where_column "
    counts_by_mapping_by_source={}
    counts_by_mapping_by_source['study'] = {}
    counts_by_mapping_by_source['ohdsi'] = {}

    for mapping in mappings:
        print("MAPPING  ({}, {}) ({}, {}) {}".format(mapping['from_table'], mapping['from_column'], mapping['vocabulary_id'], mapping['concept_code'], mapping['to_column']))

        mapping_key = (study_id, mapping['vocabulary_id'], mapping['concept_code'])

        # Sometimes you have two different study table/columns that feed into the same term in ohdsi.
        # All of ohdsi will get loaded in when you see the first and you don't want to do it again
        # when you see the second.

        # OHDSI, do only once
        if mapping_key not in list(counts_by_mapping_by_source['ohdsi'].keys()):
            counts_by_mapping_by_source['ohdsi'][mapping_key] = collections.defaultdict(int)
            for patient_id in patient_ids:
                ohdsi_rows =  get_ohdsi_rows(mapping['to_table'], mapping['to_column'], mapping['vocabulary_id'], mapping['concept_code'], patient_id, con)
                if (len(ohdsi_rows) > 0):
                    counts_by_mapping_by_source['ohdsi'][mapping_key][ohdsi_rows[0][0]] += 1

        # STUDY init the dict once, but allow each time
        if mapping_key not in list(counts_by_mapping_by_source['study'].keys()): 
            counts_by_mapping_by_source['study'][mapping_key] = collections.defaultdict(int)

        for patient_id in patient_ids:
            study_rows =  get_study_rows(study_id, patient_id, mapping['from_table'], mapping['from_column'], personObj, con)
            if (len(study_rows) > 0):
                counts_by_mapping_by_source['study'][mapping_key][study_rows[0][0]] += 1

        sys.stdout.flush()

    return counts_by_mapping_by_source

def calculate_median(map, number_values):
    """ takes a frequency distribution and finds the median.
        The map is value -> number-of-occurrences.
        Assumes positive values.
    """
    middle_index = number_values / 2;
    index_tracker=0
    median=0
    keylist = sorted(map.keys())
    last_value=0;
    prior_key = None
    for key in keylist:
        if middle_index <= index_tracker:
            # TODO not quite right... supposed to take the average when there's an even number of items.
            median = prior_key
            return  median
        else:
            index_tracker += map.get(key)
        prior_key = key
        print("key:", key, "tracker:", index_tracker, " total;", number_values, " half:", middle_index, "median:", median)

    return key

def _num_values_in_freq_dist(map):
    ''' not the number of keys, the number of values...
        This is a duplicate of logic below, needed for the test
    '''
    number_values = 0
    for value_key in map.keys():
        instance_count =  map[value_key]
        number_values += instance_count
    return number_values

def get_stats_for_column(map, column, study):
    """ tricky, the map is a count of unqique values, not per-patient:
        The keys are the values, the value of the map is the number of instances.
        It's not a raw list, its a frequency distribution."""
    sum=0
    min_value=sys.maxsize
    max_value=0
    number_values = 0 
    for value_key in map.keys():
        instance_count_value =  map[value_key]
        number_values += instance_count_value 
        try:
            sum +=  value_key * instance_count_value
        except Exception as e :
            print("ERROR Key is not int:%s value:%s column:%s study:%s", value_key, map[value_key], column, study)
            print("NB: if this is a date value, like for Kao-21, it's an unresovled edge-case in this code:dates.")
            raise e
        min_value = min(min_value, value_key)
        max_value = max(max_value, value_key)
    median_value = calculate_median(map, number_values)
    print("get_stats_for_column()", median_value, number_values, sum, map)

    return (str(min_value), str(sum/number_values), median_value, str(max_value), number_values, sum)

def print_comparison(map, conn):
    """map: (study | ohdsi) -> to_column -> value -> count
    """
    for column in map['ohdsi'].keys():
        concept_name = _get_concept_name(column, conn)    
        if (len(map['ohdsi'][column].keys()) > MAX_CONCEPTS_TO_LIST):  
            # STATS: too many values to list, run average, max, min and sdev on them.
            try:
                ohdsi_stats  = get_stats_for_column(map['ohdsi'][column], column, "ohdsi"),
                study_stats = get_stats_for_column(map['study'][column], column, "study"),
                if  (ohdsi_stats[0][0] == study_stats[0][0]
                     and abs(float(ohdsi_stats[0][1]) - float(study_stats[0][1])) < 0.0001 # TODO strings?
                     and ohdsi_stats[0][2] == study_stats[0][2]
                     and abs(float(ohdsi_stats[0][4]) - float(study_stats[0][4])) < 0.0001
                     and ohdsi_stats[0][3] == study_stats[0][3]):
                    print("OK-stats", column, concept_name, "ohdsi:", ohdsi_stats, "study:", study_stats)
                else:
                    if  (ohdsi_stats[0][0] != study_stats[0][0]):
                        print("ERROR-stats min:", column, concept_name,  "ohdsi:", ohdsi_stats[0][0], "study:", study_stats[0][0])
                    if  abs(float(ohdsi_stats[0][1]) - float(study_stats[0][1])) > 0.0001 :
                        print("ERROR-stats avg;", column, concept_name, "ohdsi:", ohdsi_stats[0][1], "study:", study_stats[0][1])
                    if ohdsi_stats[0][2] != study_stats[0][2]:
                        print("ERROR-stats med:", column, concept_name, ohdsi_stats[0][2], study_stats[0][2])
                    if abs(float(ohdsi_stats[0][4]) - float(study_stats[0][4])) > 0.0001:
                        print("ERROR-stats n:", column, concept_name, ohdsi_stats[0][4], study_stats[0][4])
                    if ohdsi_stats[0][3] != study_stats[0][3]:
                        print("ERROR-stats max:", column, concept_name, ohdsi_stats[0][3], study_stats[0][3])
            except Exception as e:
                print("ERROR:....that prior excpetion higher up, moving on to next.")
        else:
            # INSTANCES (of values, like a list of concepts or 1, 2)
            # Here you have two sets of values and respective counts from either side:
            #  map['ohdsi'][column] and map['study'][column].
            # The values may be different and the counts for each value may be different.   
            # In case of yes/no, male/female coded as 1/2, the values likely are different because they would be concept_ids in OHDSI.
            # TODO: use backwards mapping functions in migrate_functions.py to line these up.
            if len(map['ohdsi'][column].keys()) ==  len(map['study'][column].keys()) :
                print("ERROR-instances (value: count) ", column,  concept_name, "OHDSI:", map['ohdsi'][column], "STUDY:", map['study'][column])
                for count in range(0, len(map['ohdsi'][column].keys())):
                    ohdsi_key = list(map['ohdsi'][column].keys())[count]
                    ohdsi_value = map['ohdsi'][column][ohdsi_key]
                    study_key = list(map['study'][column].keys())[count] 
                    study_value = map['study'][column][study_key] # cross-contaminating keys?
                    #if ohdsi_value != study_value:
                    if (abs(ohdsi_value - study_value) > 0.0001):
                        print("ERROR-instances (value: count) ", column, concept_name, "ohdsi:", ohdsi_key, ohdsi_value, "study:", study_key, study_value)
                    else:
                        print("OK-instances", column, concept_name, "ohdsi:", ohdsi_key, ohdsi_value, "study:", study_key, study_value)
            else:
                print("ERROR-instances: different lengths of values: (AME?)", column, concept_name, end='')
                print("   ohdsi:", end='')
                for value in list(map['ohdsi'][column].keys())[:10]:
                    print((str(value), map['ohdsi'][column][value]), end='')

                print("   study:", end='') 
                for value in list(map['study'][column].keys())[:10]:
                    print("    ", (str(value), map['study'][column][value]), end='')
        print

def main(db_name, user_name, study_name) :
    conn = psycopg2.connect(database=db_name, user=user_name) 
    conn.autocommit=True;

    (study_id, observation_range_start, observation_range_end, _, _) = get_study_details(conn, study_name)

    personObj = BasePerson.factory(study_id)  
    person_ids = personObj.get_study_person_ids(conn)
    print("number of person ids:", len(person_ids))
    mappings = read_mappings(conn, study_id)
    comparison_data = build_comparison(conn, person_ids, study_id, personObj, mappings)
    print_comparison(comparison_data, conn)
    conn.close()

if __name__ == '__main__':
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)
