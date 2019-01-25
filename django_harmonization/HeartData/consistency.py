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
 consistency.py
 Python Version: 3.6.3

 After migration, this script checks for consistency between source, ohdsi and the mapping table.
 This happens in two phases so far. The first checks for schema-level consistency, and the second
 compares actual patient values.

 This is research code for demonstration purposes only.

 croeder 6/2017 chris.roeder@ucdenver.edu
'''

import logging
import datetime 
import importlib
import sys
import re
import psycopg2
from psycopg2.extras import RealDictCursor
import person 
import observation
import argh

from migrate import read_mappings
from migrate import get_mappings_by_table
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

def get_patient_visits(con, patient_id, table_name, study_id, personObj):
    """ Returns dates of patient with given a id: list of datetime.date .   
        patient_id is in the domain of our tables here and gets converted into what
        works with the study's tables.
    """ 
    cur = con.cursor(cursor_factory=RealDictCursor)
    date_column_name  = personObj.get_date_column_for_table(table_name)
    id_column_name = personObj.get_id_field_name();
    study_patient_id = personObj.convert_person_id_to_study(patient_id)
    stmt = "SELECT distinct " + date_column_name + " as date_value " \
            + "    FROM " + table_name + " t " \
            + "   WHERE " + id_column_name + " = %s"
    cur.execute(stmt, (study_patient_id,))
    date_maps =  cur.fetchall()
    cur.close()
    dates = map((lambda x: x['date_value']), date_maps)
    dates = filter(lambda x: x != None, dates)
    if  (len(date_maps) < 1 or len(list(dates)) < 1) :
        if (table_name  in BEST_exceptions):
            logger.debug("get_patient_visits() no rows returned for patient:%s, study patient_id:%s, table:%s date_column:%s", patient_id, study_patient_id, table_name, date_column_name)
        else:
            logger.error("get_patient_visits() no rows returned for patient:%s, study patient_id:%s, table:%s date_column:%s", patient_id, study_patient_id, table_name, date_column_name)
    return dates


def parse_date_string_funky_single_digit_thing(date_string): # TODO rename?, BEST specific
        # date string: 7/18/96 0:00
        if (date_string != None):
            match = re.search('(\d+)/(\d+)/(\d+)\s\d+:\d+', date_string)
            if (match != None):
                try:
                    month = int(match.group(1))
                    day  = int(match.group(2))
                    year = int(match.group(3))
                    if (year < 1900):
                        year += 1900 # TODO assumes all 2-digit dates are pre y2k
                    return datetime.datetime(year, month, day)
                except Exception as e:
                    logger.error("error in parse_date_string_funky_single_digit_thing() %s:%s, %s:%s, %s:%s    %s", month, type(month), day, type(day),  year, type(year), e);
                    return None
        else:
            logger.error("error in parse_date_string_funky_single_digit_thing() got a None input string")
            return None
            
        return None


def parse_date_string_by_dataset(date_string, dataset_name): # BEST specifc
    """ dataset_name is table names in BEST..."""
    dt = None
    if (dataset_name == "br"):
        dt = parse_date_string_funky_single_digit_thing(date_string)
        if (dt == None):
            try:
                logger.debug("trying a different date format for %s in dataset %s 1", date_string, dataset_name)
                dt =  datetime.datetime.strptime(date_string, "%Y-%m-%d 00:00:00")
            except:
                logger.error("No match in %s  by parse_date_string_by_dataset(): %s 1", date_string, dataset_name);
    else:
        try:
            dt =  datetime.datetime.strptime(date_string, "%Y-%m-%d 00:00:00")
            return dt
        except:
            dt = parse_date_string_funky_single_digit_thing(date_string)
            if (dt == None):
                logger.error("No match in '%s'  by parse_date_string_by_dataset(): %s 2", date_string, dataset_name);
            return dt
 
    return dt


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



def check_consistency(con, study_id):
    """ Check the consistency of concepts between files/columns, the mapping and the OHDSI concept table
        This is driven by entries in the mapping table, so the study may have values that we ignore if the
        mappings are not there for it. It does not check the values!
    """

    all_good=True
    mappings = read_mappings(con, study_id) 
    for row in mappings:

        num_native=0;
        num_ohdsi=0; 

        # STUDY - check that the table/column exist  as real value tables/columns
        if (row['from_table'] == 'dual') :
            rows = [row['from_column']]
        else:
            cur = con.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT \"" + row['from_column'] + "\" FROM " +  row['from_table'])
            rows = cur.fetchall()
            cur.close()
        num_native=len(rows)
        if (rows == None or len(rows) < 1):
            logger.error("Missing row in actual table for from_table:%s, from_column:%s.  STMT:%s" \
                 "(meaning, there really are mappings to nonexistant tables/colums.)",
                 row['from_table'], row['from_column'], stmt)
            all_good=False

        # OHDSI - check that the concept is there
        if (row['concept_code'] != None and row['vocabulary_id'] != None):
            try:
                stmt = ("SELECT c.* FROM concept c WHERE c.concept_code = %s AND vocabulary_id = %s ")
                cur = con.cursor(cursor_factory=RealDictCursor)
                cur.execute(stmt, (row['concept_code'], row['vocabulary_id']));
                rows = cur.fetchall()
                cur.close()
                if (len(rows) < 1):
                    logger.error("missing row in concept for from_table:%s, from_column:%s", 
                        row['vocabulary_id'], row['concept_code'])
                    all_good=False
            except:
                logger.error("missing concept:" + stmt, exc_info=True)
                all_good=False
        # else no mapping!

        # OHDSI - count how many observations there are for this concept, in this study

        # insert_ohdsi(con, mapping['to_table'], mapping['to_column'], observation_number, personObj.convert_person_id_to_ohdsi(value_row[id_column_name]), value_row['date_value'], concept_id, value)

        if (    row['concept_code'] != None and row['vocabulary_id'] != None ):
            concept_id_field_name = row['to_table'] + "_concept_id"

            stmt = ("SELECT count(*) "
                    #"FROM observation o "
                    #"JOIN concept c ON c.concept_id = o.observation_concept_id "
                    "FROM " + row['to_table'] + " o "
                    "JOIN concept c ON c.concept_id = o." + concept_id_field_name + " "
                    "  AND c.concept_code = %s "
                    "  AND c.vocabulary_id = %s "
                    "JOIN study s  ON o.person_id >= s.person_id_range_start "
                    "  AND o.person_id < s.person_id_range_end "
                    "  AND s.study_id = %s")
            cur = con.cursor()
            cur.execute(stmt, (row['concept_code'], row['vocabulary_id'], study_id ))
            rows = cur.fetchall()
            cur.close()
            num_ohdsi=rows[0][0]
            if (num_ohdsi < 1):
                logger.error("OHDSI is missing values! we have no observations %s, %d for %s %s study:%d STMT:%s", str(len(rows)), num_ohdsi, row['vocabulary_id'], row['concept_code'], study_id, stmt) 
                logger.error("   OHDSI is missing values! %s",rows) 
                all_good=False

        # count native vs count ohdsi
        # Special Case for BEST: these datasets share ohdsi terms, so you can't compare the values. It's not a 1:1 mapping, rather n:1
        canada_labs={'claalb', 'claalbx', 'clachox', 'clauax', 'clainr', 'claalt', 'claast', 'clacalx', 'clapot', 'clamag', 'clasdm', 'clachl', 
                    'clahgb', 'clabic', 'clabilx', 'claglux', 'clacre'}
        us_labs=    {'laalb', '',         'lacho',   'laua',   'lainr',  'laalt',  'laast',  'lacal',   'lapot',  'lamag',  'lasdm',  'lachl', 
                    'lahgb',  'labic',  'labil',   'laglu',   'lacre'}
        if (row['concept_code'] != None and row['vocabulary_id'] != None):
            if (row['from_column'] not in canada_labs and row['from_column'] not in us_labs ):
                if (num_native != num_ohdsi):
                    if (num_ohdsi != 0):
                        logger.warn("might want to look at (1) table:%s column:%s vocabulary:%s term:%s it has different counts for native:%d and ohdsi:%d  %f",
                            row['from_table'], row['from_column'], row['vocabulary_id'],  row['concept_code'], num_native, num_ohdsi, num_native / float(num_ohdsi));
                    else:
                        logger.warn("might want to look at (2) table:%s column:%s vocabulary:%s term:%s it has different counts for native:%d and ohdsi:%d  %d",
                            row['from_table'], row['from_column'], row['vocabulary_id'],  row['concept_code'], num_native, num_ohdsi, 0);
                else:
                    logger.info("OK table:%s column:%s vocabulary:%s term:%s it has same counts for native:%d and ohdsi:%d",
                        row['from_table'], row['from_column'], row['vocabulary_id'],  row['concept_code'], num_native, num_ohdsi);
            else :
                logger.info("labs/clabs stuff going on %s, %s  %d ohdsi:%d", row['from_table'], row['from_column'], num_native, num_ohdsi )
        else :
            logger.info("None stuff going on %s, %s", row['vocabulary_id'], row['concept_code'] )
    

    if (all_good):
        logger.info("all consistent") 
    else:
        logger.warn("all NOT consistent") 


def _get_study_rows(visit_date, patient_id, from_table, from_column, personObj, use_date_column, con):
    """ retrieves rows from study for a particular patient. Optionally resrict to a particular day.e 
    """
   # STUDY
    id_column_name = personObj.get_id_field_name();
    study_patient_id = personObj.convert_person_id_to_study(patient_id)

    cur = con.cursor(cursor_factory=RealDictCursor)
    stmt = "SELECT \"" + from_column + "\""\
        + " FROM " + from_table \
        + " WHERE " + id_column_name + " = '%s' "
    if (use_date_column):
        visit_date_column = personObj.get_date_column_for_table(from_table);
        study_date_string = format_date_string_by_dataset(visit_date, from_table) 
        stmt += " AND " + visit_date_column + " = %s"
        cur.execute(stmt, (study_patient_id, study_date_string))
    else:
        cur.execute(stmt, (study_patient_id,))
    study_rows = cur.fetchall()
    cur.close()
    return study_rows


# migrate/consistency
def check_values_are_consistent_study(con, patient_ids, study_id, personObj):
    """
        Confirms that we have source data for the mapping.
        BEST exceptions are clab1/clab2 vs lab1/lab2, and ame.
        AME doesn't have values for everyone. clab and lab are complementary.
    """

    all_good=True
    mappings = get_mappings_by_table(con, study_id)
    print("type of mappings:", type(mappings)) 

    # for each patient, for each table, for dates appropriate to that table/study/dataset...
    # ...get the values from either side and verify they are identical.
    # Complicated by different date column names and formats in different datasets in the BEST study.
    # This means you get different things out of the table when you query for them, and you have to format
    # differently when you query for the values. Mostly this is because of BR's vdate vs the others' visit_dt fields.
    for patient_id in patient_ids:
        table_counts={}
        for table in mappings.keys():
            if table not in table_counts.keys():
                table_counts[table]=0
    
                count_rows=0 
                count_worthy_rows=0
                count_comparisons=0
                count_same=0
                count_double_none=0
                for row in  mappings[table]:
                    count_rows += 1
                    if (row['concept_code'] != None and row['vocabulary_id'] != None):
                        count_worthy_rows += 1 

                        #if personObj.use_date_column_on_select(): 
                        if (row['has_date']):
                            visit_dates = get_patient_visits(con, patient_id, table, study_id, personObj)
                            for visit_date_string in visit_dates:
                                visit_date = parse_date_string_by_dataset(visit_date_string, row['from_table'])
                                if (visit_date == None):
                                    logger.error("check_values_are_consistent_study(): unparseable date string %s dataset:%s", 
                                        visit_date_string, row['from_table'])
                                else:
                                    study_rows =  _get_study_rows(visit_date, patient_id, row['from_table'], row['from_column'], personObj, True, con)
                                    if len(study_rows) > 0:
                                        table_counts[table] += 1
                                    else:
                                        logger.error("check_values_are_consistency_study(): no rows from study patient:%s visit:%s table:%s column:%s", patient_id, visit_date, row['from_table'], row['from_column']) 
                        else:
                            visit_date = None
                            study_rows =  _get_study_rows(visit_date, patient_id, row['from_table'], row['from_column'], personObj, False, con)
                            if len(study_rows) > 0:
                                table_counts[table] += 1
                            else:
                                logger.error("check_values_are_consistency_study(): no rows from study patient:%s visit:%s table:%s column:%s", patient_id, visit_date, row['from_table'], row['from_column']) 
  
            
                    if (count_worthy_rows > 0 and (count_worthy_rows != count_comparisons or count_same != count_worthy_rows)):
                        logger.debug("patient:%s, table:%s,  non-null mappings:%d comparisons:%d  rows:%d double-none:%d same:%d", 
                            patient_id, table,  count_worthy_rows, count_comparisons, count_rows, count_double_none, count_same);


        for (table_name, row_count) in table_counts.items():
            if table_name == 'best.clab1' or table_name == 'best.lab1':
                if (table_counts['best.clab1'] + table_counts['best.lab1'] < 0):
                    logger.error("short  rows for person:%d table:%s", patient_id, table_name)
            elif study_id == 1 and (table_name == 'best.clab2' or table_name == 'best.lab2'):
                # deal with canadian vs us labs in BEST
                if (table_counts['best.clab2'] + table_counts['best.lab2'] < 0):
                    logger.error("short  rows for person:%d table:%s", patient_id, table_name)
            elif (row_count == 0):
                logger.error("no rows for person:%d table:%s", patient_id, table_name)


def get_ohdsi_rows(to_table, to_column, vocabulary_id, concept_code, patient_id, visit_date):
    ohdsi_date_string = visit_date.strftime("%Y-%m-%d") 
    stmt = "SELECT " + to_column \
         + "  FROM " + to_table + " o " \
         +  "  JOIN concept c "\
         +  "    ON c.concept_id = o." + to_table + "_concept_id"\
         +  "   AND c.vocabulary_id = %s"\
         +  "   AND c.concept_code = %s"\
         +  " WHERE o.person_id = %s"\
         +  "   AND o." + to_table + "_date = %s"
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute(stmt,  (vocabulary_id, concept_code, patient_id, ohdsi_date_string))
    ohdsi_rows = cur.fetchall()
    if len(list(ohdsi_rows)) < 1:
        logger.info("consistency.get_ohdsi_rows() table:%s no rows: %s, %s, num_rows:%d", to_table, stmt, (vocabulary_id, concept_code, patient_id, ohdsi_date_string), len(list(ohdsi_rows)))
    cur.close()
    return ohdsi_rows

# migrate/consistency
def check_values_are_consistent_ohdsi(con, patient_ids, study_id, personObj):
    """
        Compare values between config and ohdsi to check the mapping
        An elaboration of the function above.
    """

    all_good=True
    mappings = get_mappings_by_table(con, study_id)

    # for each patient, for each table, for dates appropriate to that table/study/dataset...
    # ...get the values from either side and verify they are identical.
    # Complicated by different date column names and formats in different datasets in the BEST study.
    # This means you get different things out of the table when you query for them, and you have to format
    # differently when you query for the values. Mostly this is because of BR's vdate vs the others' visit_dt fields.
    term_counts= {} # (vocab, term) ->  patient_id -> count
    for patient_id in patient_ids:
        for table in mappings.keys():
            dates_per_table_with_source_values=0
            visit_dates = get_patient_visits(con, patient_id, table, study_id, personObj)

            if (len(list(visit_dates)) < 1) :
                logger.error("NO VISIT DATES len:%s table:%s  patient%s", len(list(visit_dates)), table, patient_id) 

            for visit_date_string in visit_dates:
                logger.debug("...VISIT DATE:%s patient:%s", visit_date_string, patient_id)
                count_rows=0 # TODO - trimp the mappings for unused values ahead of time instead of repeatedly checking below  $$ hash function
                count_worthy_rows=0
                count_comparisons=0
                count_same=0
                count_double_none=0
                for row in  mappings[table]:
                    if (row['vocabulary_id'], row['concept_code']) not in term_counts.keys():
                        term_counts[(row['vocabulary_id'], row['concept_code'])] = {}
                    if patient_id not in term_counts[(row['vocabulary_id'], row['concept_code'])].keys():
                        term_counts[(row['vocabulary_id'], row['concept_code'])][patient_id] = 0
                    count_rows += 1
                    if (row['concept_code'] != None and row['vocabulary_id'] != None):
                        count_worthy_rows += 1 
                        visit_date_column = 'visit_dt'
                        visit_date = parse_date_string_by_dataset(visit_date_string, row['from_table'])
                        ohdsi_value = None
                        study_value = None
  
                        if (visit_date == None):
                            logger.error("check_values_are_consistent(): unparseable date string %s dataset:%s", 
                                visit_date_string, row['from_table'])
                        else: 
            
                            # OHDSI
                            ohdsi_rows = get_ohdsi_rows(row['to_table'], row['to_column'],row['vocabulary_id'], row['concept_code'], patient_id, visit_date)
                            if (len(list(ohdsi_rows)) > 0):
                                ohdsi_value = ohdsi_rows[0][row['to_column']]
                                term_counts[(row['vocabulary_id'], row['concept_code'])][patient_id] += 1
                                logger.debug("%s GOT for vocab:%s term:%s count:%d",patient_id, row['vocabulary_id'], row['concept_code'],
                                    term_counts[(row['vocabulary_id'], row['concept_code'])][patient_id] )
                            else:
                                logger.debug("no ohdsi rows  date:%s for patient:%s vocab:%s term:%s count:%d ",
                                    visit_date_string, patient_id, row['vocabulary_id'], row['concept_code'],
                                    term_counts[(row['vocabulary_id'], row['concept_code'])][patient_id] )
                                if (row['from_column'] == 'peht'):
                                    logger.warning("(known) ohdsi lookup failed (1) date:%s patient:%s table:%s column:%s  vocab:%s term:%s. peht is non-null for only a single visit.", 
                                        visit_date_string, #visit_date,
                                         patient_id, row['from_table'], row['from_column'],
                                        row['vocabulary_id'], row['concept_code'])
                                elif (row['function_name'] == 'not_used' or row['to_table'] == None):
                                    logger.warning("(known) ohdsi lookup failed (2) date:%s patient:%s table:%s column:%s "
                                        + "vocab:%s term:%s. null to_table or function named not_used mean this isn't mapped and isn't expected to show up in ohdsi.", 
                                        ohdsi_date_string, patient_id, 
                                        row['from_table'], row['from_column'],
                                        row['vocabulary_id'], row['concept_code'])
                                else:
                                    logger.error("ohdsi lookup failed (3) date:%s patient:%s "
                                        + "table:%s column:%s vocab:%s term:%s", 
                                        visit_date_string, patient_id, 
                                        row['from_table'], row['from_column'],
                                        row['vocabulary_id'], row['concept_code'])
                                    #logger.error("  metadata:%s   STMT:%s", row, stmt)


                    if (count_worthy_rows > 0 and (count_worthy_rows != count_comparisons or count_same != count_worthy_rows)):
                        #logger.debug("patient:%s, table:%s, date:%s  non-null mappings:%d comparisons:%d  rows:%d double-none:%d same:%d", 
                        #    patient_id, table, visit_date_string, count_worthy_rows, count_comparisons, count_rows, count_double_none, count_same);
                        logger.debug("patient:%s, table:%s,  non-null mappings:%d comparisons:%d  rows:%d double-none:%d same:%d", 
                            patient_id, table,  count_worthy_rows, count_comparisons, count_rows, count_double_none, count_same);

    # raw, non-zero term counts
    for ((vocab, term), counts_by_patient) in term_counts.items(): 
        for (patient_id, count) in counts_by_patient.items():
            if count == 0:
                logger.error("check_values_are_consistent_ohdsi() %s missing for vocab:%s term:%s", patient_id, vocab, term);

    gross_term_counts = {} # how many users have used that term
    for ((vocab, term), counts_by_patient) in term_counts.items(): 
        if (vocab, term) not in gross_term_counts:
            gross_term_counts[(vocab, term)] = 0
        for (patient_id, count) in counts_by_patient.items():
            if count > 0:
                gross_term_counts[(vocab, term)] += 1

    for ((vocab, term), count) in gross_term_counts.items():
        if count < 1:
            logger.info("unused term: %s %s", vocab, term)
        if count < len(list(patient_ids)):
            logger.info("under used term: %s %s  %d %d", vocab, term, count, len(list(patient_ids)))


# migrate/consistency
def check_values_are_consistent_with_compare_count(con, patient_ids, study_id, personObj):
    """Compare values between BEST and ohdsi to check the mapping
    """

    all_good=True
    mappings = get_mappings_by_table(con, study_id)

    # for each patient, for each table, for dates appropriate to that table/study/dataset...
    # ...get the values from either side and verify they are identical.
    # Complicated by different date column names and formats in different datasets in the BEST study.
    # This means you get different things out of the table when you query for them, and you have to format
    # differently when you query for the values. Mostly this is because of BR's vdate vs the others' visit_dt fields.
    personObj = BasePerson.factory(study_id)
    term_counts= {}
    table_counts={}
    for patient_id in patient_ids:
        for table in mappings.keys():
            if table not in table_counts.keys():
                table_counts[table]=0
            dates_per_table_with_source_values=0
            visit_dates = get_patient_visits(con, patient_id, table, study_id, personObj)

            if (len(list(visit_dates)) < 1) :
                logger.error("NO VISIT DATES len:%s table:%s  patient%s", len(list(visit_dates)), table, patient_id) 

            for visit_date_string in visit_dates:
                logger.debug("...VISIT DATE:%s patient:%s", visit_date_string, patient_id)
                count_rows=0 # TODO - trimp the mappings for unused values ahead of time instead of repeatedly checking below  $$ hash function
                count_worthy_rows=0
                count_comparisons=0
                count_same=0
                count_double_none=0
                for row in  mappings[table]:
                    if (row['vocabulary_id'], row['concept_code']) not in term_counts.keys():
                        term_counts[(row['vocabulary_id'], row['concept_code'])] =0
                    count_rows += 1
                    if (row['concept_code'] != None and row['vocabulary_id'] != None):
                        count_worthy_rows += 1 
                        visit_date_column = 'visit_dt'
                        visit_date = parse_date_string_by_dataset(visit_date_string, row['from_table'])
                        ohdsi_value = None
                        study_value = None
  
                        if (visit_date == None):
                            logger.error("check_values_are_consistent(): unparseable date string %s dataset:%s", 
                                visit_date_string, row['from_table'])
                        else:
                            # STUDY 
                            study_rows =  _get_study_rows(visit_date, patient_id, row['from_table'], row['from_column'], personObj, personObj.use_date_column_on_select(), con)
                            if (len(list(study_rows)) > 0):
                                table_counts[table] += 1
                                study_value = study_rows[0][row['from_column']]
            
                            # OHDSI
                            ohdsi_rows = get_ohdsi_rows(row['to_table'], row['to_column'],row['vocabulary_id'], row['concept_code'], patient_id, visit_date)
                            if (ohdsi_rows != None and len(list(ohdsi_rows)) > 0):
                                ohdsi_value = ohdsi_rows[0][row['to_column']]
                                term_counts[(row['vocabulary_id'], row['concept_code'])] += 1
                                logger.debug("%s GOT for vocab:%s term:%s count:%d",patient_id, row['vocabulary_id'], row['concept_code'],
                                    term_counts[(row['vocabulary_id'], row['concept_code'])] )
                            else:
                                logger.info("date:%s FAIL (got no rows) for patient:%s vocab:%s term:%s count:%d ",
                                    visit_date_string, patient_id, row['vocabulary_id'], row['concept_code'],
                                    term_counts[(row['vocabulary_id'], row['concept_code'])])
                                if (row['from_column'] == 'peht'):
                                    logger.warning("(known) ohdsi lookup failed (4) date:%s patient:%s table:%s column:%s  vocab:%s term:%s. peht is non-null for only a single visit.", 
                                        visit_date_string, #visit_date,
                                         patient_id, row['from_table'], row['from_column'],
                                        row['vocabulary_id'], row['concept_code'])
                                elif (row['function_name'] == 'not_used' or row['to_table'] == None):
                                    logger.warning("(known) ohdsi lookup failed (5)  date:%s patient:%s table:%s column:%s "
                                        + "vocab:%s term:%s. null to_table or function named not_used mean this isn't mapped and isn't expected to show up in ohdsi.", 
                                        ohdsi_date_string, patient_id, 
                                        row['from_table'], row['from_column'],
                                        row['vocabulary_id'], row['concept_code'])
                                else:
                                    logger.error("ohdsi lookup failed (6) date:%s patient:%s "
                                        + "table:%s column:%s vocab:%s term:%s", 
                                        visit_date_string, patient_id, 
                                        row['from_table'], row['from_column'],
                                        row['vocabulary_id'], row['concept_code'])


                        # COMPARE/COUNT
                        count_comparisons += 1
                        if (study_value == None and ohdsi_value == None):
                            count_double_none += 1
                            #
                        elif (str(study_value) == str(ohdsi_value)): 
                            count_same += 1
                            logger.debug("SAME patient id: %s, date:%s, table:%s column:%s study:%s, ohdsi:%s", 
                                patient_id, visit_date_string, row['from_table'], row['from_column'], study_value, ohdsi_value)
                        elif (study_value != None and ohdsi_value != None):
                            if (study_value == None):
                                logger.error("  check_consistency() study value: %s came up None. %s %s pid:%s  %s ohdsi:%s", 
                                    study_value, row['from_table'], row['from_column'], patient_id, study_date_string, ohdsi_value);
                            elif (ohdsi_value == None):
                                logger.error("  check_consistency() ohdsi value:%s came up None. %s %s pid:%s   %s study:%s", 
                                    ohdsi_value, row['vocabulary_id'], row['concept_code'], patient_id, str(visit_date_string), study_value);
                            elif (str(study_value) != str(ohdsi_value)):
                                logger.error("  DIFFERENT VALUES for from:%s/%s to:%s/%s are study:%s and ohdsi:%s  date:%s patient:%s", 
                                    row['from_column'], row['from_table'], row['vocabulary_id'], row['concept_code'], 
                                    study_value, ohdsi_value,
                                    visit_date_string, patient_id)
                            else:
                                # shouldn't happen. This does happen when you have the same (more/less) value, but different types
                                logger.error("ELSE: '%s':%s  '%s':%s this should not happen (see code)", study_value, type(study_value), ohdsi_value, type(ohdsi_value))
                        #elif (study_value == None and ohdsi_value != None):
                            #logger.info(" None and not-None");
                        #elif (study_value != None and ohdsi_value == None):
                            #logger.info(" Not-none and None");
                        #else:
                            #logger.info("should never happen?"); # TODO

                    if (count_worthy_rows > 0 and (count_worthy_rows != count_comparisons or count_same != count_worthy_rows)):
                        #logger.debug("patient:%s, table:%s, date:%s  non-null mappings:%d comparisons:%d  rows:%d double-none:%d same:%d", 
                        #    patient_id, table, visit_date_string, count_worthy_rows, count_comparisons, count_rows, count_double_none, count_same);
                        logger.debug("patient:%s, table:%s,  non-null mappings:%d comparisons:%d  rows:%d double-none:%d same:%d", 
                            patient_id, table,  count_worthy_rows, count_comparisons, count_rows, count_double_none, count_same);

        for (vocab, term) in term_counts.keys(): 
            if term_counts[(vocab, term)] == 0:
                logger.error("check_values_are_consistent_with_compare_count() %s missing for vocab:%s term:%s", patient_id, vocab, term);

                if (dates_per_table_with_source_values < 1) :
                    logger.warning("no data on any day for table:%s patient:%s dates:%s",  table, patient_id, visit_dates)



        



def main(db_name, user_name, study_name) :
    conn = psycopg2.connect(database=db_name, user=user_name) 
    conn.autocommit=True;

    (study_id, observation_range_start, observation_range_end, _, _) = get_study_details(conn, study_name)

    personObj = BasePerson.factory(study_id)  
    person_ids = personObj.get_study_person_ids(conn)
    mappings = read_mappings(conn, study_id)

    logger.info("CHECKING 1 (mapping)")
    check_consistency(conn, study_id)

    logger.info("CHECKING 2 (study-side)")
    check_values_are_consistent_study(conn, person_ids, study_id, personObj)

    logger.info("CHECKING 3 (ohdsi-side) ")
    check_values_are_consistent_ohdsi(conn, person_ids, study_id, personObj)
    print("\n\n\n---------------------- COUNTS FOLLOW ----------------------\n\n\n")

    logger.info("CHECKING 4 (study-to-ohdsi) ")
    check_values_are_consistent_with_compare_count(conn, person_ids, study_id, personObj)

    conn.close()


if __name__ == '__main__':
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)
    
