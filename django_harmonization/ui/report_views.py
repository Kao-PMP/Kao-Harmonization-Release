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
 report_views.py <db> <user>
 Python Version: 3.6.3

 croeder 3/2018 chris.roeder@ucdenver.edu
    cribbed from report.py
'''

import psycopg2
from psycopg2.extras import RealDictCursor
from HeartData.study import get_study_details

class StudyValueSerializer(serializers.Serializer):
        id = serializers.CharField(max_length=100);
        value = serializers.CharField(max_length=100);
        from_table = serializers.CharField(max_length=100);
        from_column = serializers.CharField(max_length=100);

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

    # SERIALIZE
    json_list=list()
    for row in rows:
        print("DEBUG: get_study_values() ROW", row)
        serializer = StudyValueSerializer(row)
        serialized = serializer.data
        print("DEBUG: get_study_values() SER",  serialized)
        json_list.append(serialized)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json


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

## TODO ohdsi_calculated_table

def report_calculated_concepts(con, study_id):
    '''  join the configuration of mapping together and produce/print a report '''
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
    return(rows)


def extract_function_parameters(con, function_name, long_name, rule_id):
    '''  fetch the parameters to go with an extraction function '''
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
    return(rows)

class MappedConceptsSerializer(serializers.Serializer):
        study_id
        from_table as m_from_table
= serializers.CharField(max_length=100);
        from_column as m_from_column
= serializers.CharField(max_length=100);
        function_name as m_function_name
= serializers.CharField(max_length=100);
        vocabulary_id as vocab
= serializers.CharField(max_length=100);
        concept_code as concept
= serializers.CharField(max_length=100);
        to_table as m_to_table
= serializers.CharField(max_length=100);
        to_column as m_to_column
= serializers.CharField(max_length=100);
        from_table as c_from_table
= serializers.CharField(max_length=100);
        function_name as c_function_name
= serializers.CharField(max_length=100);
        long_name as c_long_name
= serializers.CharField(max_length=100);
        rule_id 
        id 
= serializers.CharField(max_length=100);
        value = serializers.CharField(max_length=100);
        from_table = serializers.CharField(max_length=100);
        from_column = serializers.CharField(max_length=100);

def report_mapped_concepts(con, study_id):
    ''' report and print the configuration 
        joins on categorization_function_metadata so it only shows 
        concepts used by direct extraction/categorization
    '''
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT "
            "m.study_id, "
            "m.from_table as m_from_table, "
            "m.from_column as m_from_column, "
            "m.function_name as m_function_name, "
            "m.vocabulary_id as vocab, "
            "m.concept_code as concept, "
            "m.to_table as m_to_table, "
            "m.to_column as m_to_column, "
            "c.from_table as c_from_table, "
            "c.function_name as c_function_name, "
            "c.long_name as c_long_name,"
            "c.rule_id "
            "FROM study_to_ohdsi_mapping m, categorization_function_metadata c "
            "WHERE m.study_id = %s "
            "AND m.function_name is not null "
            "AND m.vocabulary_id = c.from_vocabulary_id "
            "AND m.concept_code = c.from_concept_code "
            "ORDER BY m.study_id, c.long_name;")
    cur.execute(stmt, (study_id,))
    rows = cur.fetchall()

    # SERIALIZE
    json_list=list()
    for row in rows:
        print("DEBUG: get_study_values() ROW", row)
        serializer = StudyValueSerializer(row)
        serialized = serializer.data
        print("DEBUG: get_study_values() SER",  serialized)
        json_list.append(serialized)
    return(JsonResponse(json_list, safe=False, status=200)) # JsonResponse application/json

def report_unmapped_concepts(con, study_id):
    ''' report and print the configuration 
        doesn't have the jion as above, lists concepts that might be used
        as input to further calculation
    '''
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
    return(rows)

def report_calculated_extraction(con, study_id, extract_study_id):
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
    return(rows)


def report_events_mapping(con, study_id):
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT from_table, from_column, value_vocabulary_id, value_concept_code, to_table, to_column, from_date_column, where_clause, comment "
            "  FROM events_mapping "
            " WHERE study_id = %s")
    cur.execute(stmt, (study_id,))
    rows = cur.fetchall()
    return(rows)

def report_wide_extraction(con, extract_study_id):
    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = ("SELECT from_table, from_column, from_vocabulary_id, from_concept_code, function_name, long_name "
            "  FROM categorization_function_table "
            " WHERE extract_study_id = %s")
    cur.execute(stmt, (extract_study_id,))
    rows = cur.fetchall()
    return(rows)

def get_study_name(con, study_id) :
    cur = con.cursor()
    stmt = "SELECT study_name FROM study WHERE study_id = %s"
    print(type(study_id))
    print(study_id)
    cur.execute(stmt, (study_id, ))
    rows = cur.fetchall()

def get_study_details(con, name) :
    ''' returns (study_id, observation_range_start, observation_range_end, person_id_range_start, person_id_range_end ) given a study name
        raises if it can't find the study name
    ''' 
    cur = con.cursor()
    stmt = "SELECT study_id, observation_range_start, observation_range_end, person_id_range_start, person_id_range_end FROM study WHERE study_name = %s"
    cur.execute(stmt, (name,))
    rows = cur.fetchall()
        
