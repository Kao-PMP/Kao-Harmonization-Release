#!/usr/bin/env python3
''' This script shows what variables the different studies import with no bearing on extract configuration or calculation. 
    Different output formats are available:
        availability grid shows just an 'x'.
        CSV and TXT show the source columns, not just the concepts and names.
'''
        
import argh
import psycopg2
import logging
import os

DBNAME=os.environ.get('PGDATABASE'),
USERNAME=os.environ.get('PGUSER'),
PASSWORD=os.environ.get('PGPASSWORD'),
HOST=os.environ.get('PGHOST'),
PORT=os.environ.get('PGPORT'),

logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name

# builds a super map of (vocab, concept, concept_name) keys to [study_id, from_table, from_column} lists
# the key is technically just vocab and concept, but adding concept_name there is convenient
 
def _lookup_concept_name(vocab_id, concept_code, cur):
    stmt = "SELECT concept_name, concept_code FROM concept where vocabulary_id = %s and concept_code = %s"
    cur.execute(stmt, (vocab_id, concept_code))
    rows = cur.fetchall()
    if (len(rows) > 0): 
        #return(rows[0][0] + " " + rows[0][1])
        return(rows[0][0])
    else:
        return('')


def _fetch_study_data(study_id, cur):
    # Returns a map, keyed by a pair/tuple (vocabulary, concept), of table, column and transformation function names.
    # ...for the given study.
    map = {}
    stmt = """
            SELECT sm.vocabulary_id, sm.concept_code, sm.from_table, sm.from_column, sm.function_name, s.study_name, c.concept_name
            FROM study_to_ohdsi_mapping sm, study s, concept c
            WHERE s.study_id = %s 
            AND s.study_id = sm.study_id
            AND sm.vocabulary_id = c.vocabulary_id
            AND sm.concept_code = c.concept_code
            ORDER BY sm.concept_code
            ;"""
    cur.execute(stmt, [study_id])
    cfg_rows = cur.fetchall()
    for crow in cfg_rows:
        map[(crow[0], crow[1], crow[6])] = { "study_name":crow[5], "from_table":crow[2], "from_column":crow[3], "function_name":crow[4] }

    return map


def _print_cfg(concept_keys, value_maps, cfg):
    # value_maps AKA study_maps

    (name_keys, column_keys) = cfg

    # Header 
    # concept_column headers
    for nkey in name_keys:
        print(f"{nkey[0]: <{nkey[1]}}", end=nkey[2])
    # value headers
    for study_id in value_maps.keys():
        for ckey in column_keys:
            #arbitrary_concept_key = list(value_maps[study_id].keys())[0]
            arbitrary_concept_key = next(iter(value_maps[study_id].keys()))
            study_name = value_maps[study_id][arbitrary_concept_key]['study_name']
            print(f"{study_name +  ' ' + ckey[0]: <{ckey[1]}}", end=ckey[2])
    print('')

    # Data
    for concept_key in concept_keys :
        # concept columns come first
        i =0
        for name_part in name_keys:
            name_width = name_part[1] -1
            print(f'{concept_key[i][0:name_width]: <{name_part[1]}}', end=name_part[2])
            i = i + 1

        # values repeated for each study next
        for study_id in value_maps.keys():
            if (concept_key in value_maps[study_id].keys()):
                stuff = value_maps[study_id][concept_key]
                for ckey in column_keys:
                    print(f'{stuff[ckey[0]]: <{ckey[1]}}', end=ckey[2]) 
            else:
                for ckey in column_keys:
                    print(f"{'NA': <{ckey[1]}}", end=ckey[2]) 
                
        print('')

def _calculate_concept_fractions(concept_keys, study_maps):
    # what fraction of studies have this concept?
    concept_counts={}
    for concept_key in concept_keys:
        count = 0 
        for study_id in study_maps.keys():
            if concept_key in study_maps[study_id]:
                count = count + 1
        concept_counts[concept_key] = count
    return concept_counts

def _calculate_study_fractions(concept_keys, study_maps):
    # what fraction of concepts does each study have?
    study_names={}
    study_var_counts = {}
    for study_id in study_maps.keys():
        study_var_counts[study_id]=0

    for study_id in study_maps.keys():
        #first_study_concept_key = list(study_maps[study_id].keys())[0]
        first_study_concept_key = next(iter(study_maps[study_id].keys()))
        ##first_study_concept_key = study_maps[study_id].keys()
        study_names[study_id]=study_maps[study_id][first_study_concept_key]['study_name']
        for concept_key in concept_keys:
            if concept_key in study_maps[study_id]:
                study_var_counts[study_id] = study_var_counts[study_id]  + 1

    return (study_var_counts, study_names)

def _print_study_count(concept_keys, study_counts, study_names):
    total = len(concept_keys)
    for study_id in study_counts.keys():
        print(f'{study_id: <3} {study_names[study_id]: <15} {study_counts[study_id]:4.0f} of {total:4.0f} {(study_counts[study_id] / total)*100: 3.0f}%')


def _display_grid(concept_keys, maps) :

    # Header
    print(f"{'vocab_id': <10}", end='')
    print(f"{'concept_code':<15}", end='')
    print(f"{'concept_name': <22}", end='')

    for study_id in maps.keys():
        print(f"{study_id: >3}",end='')
    print('')

    # Data
    for concept_key in concept_keys:
        vocab_id = concept_key[0]
        concept_code = concept_key[1]
        concept_name = concept_key[2]

        print(f'{vocab_id: <10}', end='') 
        print(f'{concept_code: <15}', end='') 
        print(f'{concept_name[0:20]: <22}', end='') 

        for study_id in maps.keys():
            if concept_key in maps[study_id]:
                #print(maps[study_id][concept_key], end='')
                print("  x", end = '')
            else:
                print("   ", end='')
        print("")

    


# report type can be one of 'CSV', 'TXT', or 'GRID'
def main(report_type):

    db_name=os.environ.get('PGDATABASE')
    user_name=os.environ.get('PGUSER')

    con = psycopg2.connect(database=db_name, user=user_name) 
    con.autocommit=True;
    cur = con.cursor()

    try:
        study_maps={}  # a vector of dictionaries
        
        key_set = {} # for building a set of the keys, using a dictionary as set 
        #stmt = "SELECT study_id, study_name FROM study where study_name not in ('NULL', 'TEST') order by study_id;"
        stmt = "SELECT study_id, study_name FROM study WHERE study_name not in ('NULL', 'TEST', 'BEST','HFACTION', 'SCDHEFT', 'PARADIGM', 'ATMOSPHERE', 'CORONA', 'IPRESERVE' )  ORDER BY study_id;"
        cur.execute(stmt)
        study_rows = cur.fetchall()
        for row in study_rows:
            study_id = row[0]
            study_maps[study_id] = _fetch_study_data(study_id, cur)
            # combines the values of like-keyed 
            key_set = {**key_set, **study_maps[study_id]}
    
        if report_type == 'GRID':
            _display_grid(key_set.keys(), study_maps)

        if report_type == 'CSV':
            csv_cfg = ([('short_name', 0, ','), ('vocabulary_id', 0, ','), ('concept_code', 0, ',')],
                       [('from_table',0, ','), ('from_column', 0, ',')])
            _print_cfg(key_set.keys(), study_maps, csv_cfg)
    
        if report_type == 'TXT':
            txt_cfg = ([('vocabulary_id', 15, ''), ('concept_code', 16, '') ,  ('concept_name', 20, '')],  
                       [('from_table', 45, ''), ('from_column', 24, '')] )
            _print_cfg(key_set.keys(), study_maps, txt_cfg)

        # per-study ratio of number of imported  concepts to total in system
        print('')
        (study_counts, study_names) = _calculate_study_fractions(key_set.keys(), study_maps)
        _print_study_count(key_set.keys(), study_counts, study_names)
        

        # per-concept ratio of number of studies
        print('')
        concept_study_counts = _calculate_concept_fractions(key_set.keys(), study_maps)
        total = len(study_maps.keys())
        for concept in concept_study_counts:
            print(f'{concept[0]:<10} {concept[1]:<15} {concept[2][:28]:<30} {(concept_study_counts[concept]/total)*100: >3.0f}%')

        
        con.close()

    except Exception as ex:
        logger.error(ex)
        con.close()
        raise ex
    

if __name__ == '__main__':
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)
