#!/usr/bin/env python3
''' Driven by an export configuration, this script shows what variables the different studies have.
    Different output formats are available:
        availability grid shows just an 'x'.
        CSV and TXT show the source columns, not just the concepts and names.

'''
        
import argh
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
from HeartData.person import BasePerson
from HeartData.person import BASE_DATE


DBNAME=os.environ.get('PGDATABASE'),
USERNAME=os.environ.get('PGUSER'),
PASSWORD=os.environ.get('PGPASSWORD'),
HOST=os.environ.get('PGHOST'),
PORT=os.environ.get('PGPORT'),

logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name


def _lookup_concept_in_calculation(vocab_id, concept_code, cur):
    tuple = _lookup_concept_in_calculation_tuple(vocab_id, concept_code, cur)
    if tuple: 
        return('(' + tuple[0] + ', ' +  tuple[1] + ', ' + tuple[2] + ', ' + tuple[3] + ')')
    else:
        return('')

def _lookup_concept_in_calculation_tuple(vocab_id, concept_code, cur):
    stmt = """  SELECT o.study_id, o.to_vocabulary_id, o.to_concept_code, c.concept_name 
                FROM ohdsi_calculation_argument o, concept c  
                WHERE o.vocabulary_id = %s and o.concept_code = %s 
                AND c.vocabulary_id = o.to_vocabulary_id 
                AND c.concept_code = o.to_concept_code 
            """
    cur.execute(stmt, (vocab_id, concept_code))
    rows = cur.fetchall()
    if len(rows) > 0:
        return((rows[0][3], str(rows[0][0]), rows[0][1], rows[0][2]))
    else:
        return None

       
def _get_study_mappings_by_extract_study(extract_study_id, cur, dict_cur): 

    study_mappings= {} # a dictionary by study_id of dictionaries by (vocabulary_id, concpet_code) pairs

    super_key_set = set() # for getting a superset of the (vocab, concept) keys
    stmt = """ SELECT study_id, study_name 
               FROM study 
               WHERE study_name not in ('BEST-101', 'NULL', 'TEST', 'HFACTION', 'TOPCAT', 'BEST', 'SCDHEFT', 'PARADIGM', 'ATMOSPHERE', 'CORONA', 'IPRESERVE' )
               ORDER BY study_id;
           """


    cur.execute(stmt)
    study_rows = cur.fetchall()
    for row in study_rows:
        study_id = row[0]
        study_mappings[study_id] = _fetch_study_mapping(study_id, dict_cur)
        super_key_set = super_key_set | set(study_mappings[study_id].keys())

    return (study_mappings, super_key_set)


def _get_categorization_parameters_for_extract_study(extract_study_id, dict_cur):
    """
        returns a dictionary keyed by (vocabulary_id, concept_code) of lists of rows. 
        The rows are dictionaries as those returned by a dict_cur. 

        param extract_study_id
        Returns dictionary keyed by (vocabulary_id, concept_code) ->  list of row-dicts
           the keys for the attributes are: 
        (from_vocabulary_id, from_concept_code, short_name, function_name, value_limit, rank, vocabulary_id, concept_name)
    """

    calc_map = {}
    stmt = """  SELECT m.from_vocabulary_id, m.from_concept_code, m.short_name, 
                m.function_name, p.value_limit, p.rank, c.vocabulary_id, c.concept_code, c.concept_name
                FROM categorization_function_metadata m 
                LEFT JOIN categorization_function_parameters p 
                  ON  m.extract_study_id = p.extract_study_id
                  AND m.function_name = p.function_name
                  AND m.long_name = p.long_name
                  AND m.rule_id = p.rule_id
                LEFT JOIN concept c
                  ON p.from_concept_id = c.concept_id
                WHERE m.extract_study_id =  %s
                 ORDER BY sequence, rank ;
            """
            ## --  AND m.rank = p.rank

    dict_cur.execute(stmt, [extract_study_id])
    rows = dict_cur.fetchall()
    
    for row in rows:
        if (row['from_vocabulary_id'], row['from_concept_code']) not in calc_map:
            calc_map[(row['from_vocabulary_id'], row['from_concept_code'])] = []
        calc_map[(row['from_vocabulary_id'], row['from_concept_code'])].append(row)

    return calc_map

# restricted to exported/extracted concepts only
def get_study_calculations_map(study_id, extract_study_id, cur):
    stmt = """ SELECT distinct  o.to_vocabulary_id, o.to_concept_code, o.function_name, c.short_name, sequence
               FROM ohdsi_calculation_function o
               LEFT OUTER JOIN  categorization_function_metadata c
                 ON  c.from_vocabulary_id = o.to_vocabulary_id
                 AND c.from_concept_code = o.to_concept_code
                 AND c.extract_study_id = %s
               WHERE o.study_id = %s 
               ORDER BY  sequence
            """
    cur.execute(stmt, [extract_study_id, study_id])
    rows = cur.fetchall()

    calc_map={}
    for row in rows:
        calc_map[(row[0], row[1])] =  row
    return calc_map


def get_calculation_arguments(study_id, extract_study_id, der_vocab_id, der_concept_code, cur):
    stmt_outer = """  SELECT a.vocabulary_id, a.concept_code, c.concept_name , m.short_name,
                        a.argument_name, a.argument_order, value_field
                FROM ohdsi_calculation_argument a
                LEFT OUTER JOIN  categorization_function_metadata m
                  ON m.from_vocabulary_id = a.vocabulary_id
                  AND m.from_concept_code = a.concept_code
                  AND m.extract_study_id = %s -- must be inside the join clause else a non-null comes into play and breaks the whole outer join thing
                LEFT OUTER JOIN concept c
                  ON c.vocabulary_id = a.vocabulary_id 
                  AND c.concept_code = a.concept_code 
                WHERE a.to_vocabulary_id = %s 
                  AND a.to_concept_code = %s 
                  AND a.study_id = %s
            """
    cur.execute(stmt_outer, (extract_study_id, der_vocab_id, der_concept_code, study_id))
    rows = cur.fetchall()
    return rows


def _lookup_concept_in_calculation_tuple_study(vocab_id, concept_code, study_id, cur):
    stmt = """  SELECT o.study_id, o.to_vocabulary_id, o.to_concept_code, c.concept_name 
                FROM ohdsi_calculation_argument o, concept c  
                WHERE o.vocabulary_id = %s and o.concept_code = %s 
                AND c.vocabulary_id = o.to_vocabulary_id 
                AND c.concept_code = o.to_concept_code 
                AND o.study_id = %s"""
    cur.execute(stmt, (vocab_id, concept_code, study_id))
    rows = cur.fetchall()
    if len(rows) > 0:
        return((rows[0][3], str(rows[0][0]), rows[0][1], rows[0][2]))
    else:
        return None

def _lookup_concept_name(vocab_id, concept_code, cur):
    stmt = "SELECT concept_name from concept where vocabulary_id = %s and concept_code = %s"
    cur.execute(stmt, (vocab_id, concept_code))
    rows = cur.fetchall()
    if len(rows) > 0 and len(rows[0]) > 0 : 
        return(rows[0][0])
    else:
        return('')

def _lookup_concept_name_by_id(concept_id, cur):
    stmt = "SELECT concept_name from concept where concept_id = %s"
    cur.execute(stmt, [concept_id])
    rows = cur.fetchall()
    if len(rows) > 0 and len(rows[0]) > 0 : 
        return(rows[0][0])
    else:
        return('')

def _lookup_concept_name_dict_cur(vocab_id, concept_code, dict_cur):
    stmt = "SELECT concept_name from concept where vocabulary_id = %s and concept_code = %s"
    dict_cur.execute(stmt, (vocab_id, concept_code))
    rows = dict_cur.fetchall()
    if len(rows) > 0 and len(rows[0]) > 0 : 
        return(rows[0]['concept_name'])
    else:
        return('')


def _lookup_study_name(study_id, cur):
    stmt = "SELECT study_name from study where study_id = %s"
    cur.execute(stmt, [study_id])
    rows = cur.fetchall()
    if (len(rows) > 0): 
        return(rows[0][0])
    else:
        return('')

def is_derived_variable(study_id, vocabulary_id, concept_code, cur):
    stmt = """  SELECT  count(*)
                FROM ohdsi_calculation_function
                WHERE  study_id = %s
                AND    to_vocabulary_id = %s 
                AND    to_concept_code = %s 
           """
    cur.execute(stmt, (study_id, vocabulary_id, concept_code))
    rows = cur.fetchall()
    if len(rows) > 0 and rows[0][0] > 0:
        return(rows[0][0])
    else:
        return None

def _fetch_extracted_names(extract_study_id, cur):
    """ Returns a map, keyed by a pair/tuple (vocabulary, concept), of short and long names as well as the concept name from OMOP.
        for the given extract_study_id.
        TODO Just us a DictCURSOR???
    """
    names_map = {}

    if extract_study_id:
        stmt = """
            SELECT cfm.from_vocabulary_id, cfm.from_concept_code, cfm.long_name, cfm.short_name, c.concept_name, sequence
            FROM categorization_function_metadata cfm, concept c
            WHERE cfm.extract_study_id = %s
            AND cfm.from_vocabulary_id = c.vocabulary_id
            AND cfm.from_concept_code = c.concept_code
            ORDER BY sequence;
            """
        cur.execute(stmt, [extract_study_id])
    else :
        stmt = """
            SELECT cfm.from_vocabulary_id, cfm.from_concept_code, cfm.long_name, cfm.short_name, c.concept_name, sequence
            FROM categorization_function_metadata cfm, concept c
            WHERE cfm.from_vocabulary_id = c.vocabulary_id
            AND cfm.from_concept_code = c.concept_code
            ORDER BY sequence;
            """
        cur.execute(stmt)
    cfg_rows = cur.fetchall()
    for crow in cfg_rows:
        names_map[(crow[0], crow[1])] = { "vocabulary_id":crow[0], "concept_code":crow[1], 
                                            "long_name":crow[2], "short_name":crow[3], 
                                            "concept_name":crow[4] }

    return names_map


def _fetch_study_mapping(study_id, dict_cur):
    """ Returns a map, keyed by a pair/tuple (vocabulary, concept), of table, column and transformation function names.
        ...for the given study.
    """
    map = {}
    stmt = """
            SELECT sm.vocabulary_id, sm.concept_code, sm.from_table, sm.from_column, 
                sm.function_name, s.study_name, sm.comment, sm.units, sm.has_date,
                sm.from_where_clause, from_where_column
            FROM study_to_ohdsi_mapping sm, study s
            WHERE s.study_id = %s 
            AND s.study_id = sm.study_id;"""
    dict_cur.execute(stmt, [study_id])
    cfg_rows = dict_cur.fetchall()
    for crow in cfg_rows:
        #map[(crow[0], crow[1])] = { "study_name":crow[5], "from_table":crow[2], "from_column":crow[3], "function_name":crow[4] }
        map[(crow['vocabulary_id'], crow['concept_code'])] = crow

    return map

# assumes a single row
def _fetch_study_source_location_by_concept(study_id, vocabulary_id, concept_code, cur):
    stmt = """
            SELECT s.vocabulary_id, s.concept_code, s.from_table, s.from_column, s.function_name
            FROM study_to_ohdsi_mapping s
            WHERE s.study_id = %s 
              AND s.vocabulary_id = %s
              AND s.concept_code = %s
        """
    cur.execute(stmt, [study_id, vocabulary_id, concept_code])
    cfg_rows = cur.fetchall()
    for crow in cfg_rows:
        return [crow[2], crow[3], crow[4] ]

def _fetch_study_mapping_arguments(study_id, from_table, from_column, function_name , dict_cur):
    stmt = """ SELECT 
                      mapped_string, mapped_number, mapped_concept_vocabulary_id, mapped_concept_code, 
                      transform_factor, transform_shift,
                      to_concept_vocabulary_id, to_concept_code
               FROM study_mapping_arguments
               WHERE study_id = %s  
                AND  from_table = %s AND from_column = %s
                AND  function_name = %s
              ORDER BY mapped_string, mapped_number
           """
    dict_cur.execute(stmt, [study_id, from_table, from_column, function_name])
    return dict_cur.fetchall()


def create_arguments_html(study_id, vocabulary_id, concept_code, from_table, from_column, function_name, dict_cur):
    """ Creates a sub-table for this study
        Param study_id
        Param vocabulary_id
        Param concept_code
        Param from_table
        Param function_name
        Param dict_cur, a django dictionary cursor
        Returns a map from study_id to table of arguments

        select from_table, from_column, function_name, mapped_string, mapped_number, transform_factor, transform_shift, to_concept_vocabulary_id, to_concept_code 
        from study_mapping_arguments 
        where study_id = 24;
    
        return "{} {} {}    {} {} {}".format(study_id, vocabulary_id, concept_code, stuff['from_table'], stuff['from_column'], stuff['function_name'])
    """

    argument_rows = _fetch_study_mapping_arguments(study_id, from_table, from_column, function_name, dict_cur)
    if len(argument_rows) == 0 and (function_name == 'map_number' or function_name == 'map_string'):
        return ['*** Missing ARGS?! ***']

    
    table_string='<table valign="top">' # border="1" width="100%" height="100%">'
    for arg_row in argument_rows:
        concept_name =  _lookup_concept_name_dict_cur(arg_row['to_concept_vocabulary_id'], arg_row['to_concept_code'], dict_cur)[:20]
        text_string="<tr><td style=\"white-space:nowrap\" >"

        if function_name == 'map_string':
            text_string = text_string + "{} &#8594 ({}, {})".format(
                arg_row['mapped_string'], 
                arg_row['to_concept_vocabulary_id'], 
                arg_row['to_concept_code'])
            text_string = text_string + " \"" + concept_name + "\""
        elif function_name == 'map_concept':
            text_string = text_string + "from: {}, {} to:({}, {)}".format(
                arg_row['mapped_concept_vocabulary_id'], 
                arg_row['mapped_concept_code'], 
                arg_row['to_concept_vocabulary_id'], 
                arg_row['to_concept_code'])
            text_string = text_string + " \"" + concept_name +"\""
        elif function_name == 'map_number':
            text_string = text_string + "{} &#8594 ({}, {})".format(arg_row['mapped_number'], arg_row['to_concept_vocabulary_id'], arg_row['to_concept_code'])
            text_string = text_string + " \"" + concept_name + "\""
        elif function_name == 'not_null_number':  ## TODO !!! this display stuff belongs with the functions, not way out here
            value_flag='x?x'
            if arg_row['mapped_number'] == -1.0:
                value_flag = 'null'
            elif arg_row['mapped_number'] == 0.0:
                value_flag = '0'
            elif arg_row['mapped_number'] > 0.0:
                value_flag = '>0'
            text_string = text_string + "{} &#8594 ({}, {})".format(value_flag, arg_row['to_concept_vocabulary_id'], arg_row['to_concept_code'])
            text_string = text_string + " \"" + concept_name +"\""
        elif function_name == 'linear_equation':
            text_string = text_string + "factor {} shift:{}".format(arg_row['transform_factor'], arg_row['transform_shift'])

        text_string = text_string + "</td></tr>"

        table_string = table_string + text_string

    table_string = table_string + "</table>"
    return table_string


def create_arguments_text(study_id, vocabulary_id, concept_code, from_table, from_column, function_name, dict_cur):
    """ Create a list of strings, each describing an argument related to a mapping for the (study, vocabulary, concept)
        Param study_id
        Param vocabulary_id
        Param concept_code
        Param from_table
        Param function_name
        Param dict_cur, a django dictionary cursor

        select from_table, from_column, function_name, mapped_string, mapped_number, transform_factor, transform_shift, to_concept_vocabulary_id, to_concept_code 
        from study_mapping_arguments 
        where study_id = 24;
    
        return "{} {} {}    {} {} {}".format(study_id, vocabulary_id, concept_code, stuff['from_table'], stuff['from_column'], stuff['function_name'])
    """


    text_list=[] # 
    argument_rows = _fetch_study_mapping_arguments(study_id, from_table, from_column, function_name, dict_cur)
    if len(argument_rows) == 0 and (function_name == 'map_number' or function_name == 'map_string'):
        return ['*** Missing ARGS?! ***']

    for arg_row in argument_rows:
        text_string=''
        concept_name =  _lookup_concept_name_dict_cur(arg_row['to_concept_vocabulary_id'], arg_row['to_concept_code'], dict_cur)[:20]

        if function_name == 'map_string':
            text_string = "{} &#8594 ({},{})".format(
                arg_row['mapped_string'], 
                arg_row['to_concept_vocabulary_id'], 
                arg_row['to_concept_code'])
            text_string = text_string + " \"" + concept_name + "\""
        elif function_name == 'map_concept':
            text_string = "from: {},{} to:({}, {)}".format(
                arg_row['mapped_concept_vocabulary_id'], 
                arg_row['mapped_concept_code'], 
                arg_row['to_concept_vocabulary_id'], 
                arg_row['to_concept_code'])
            text_string = text_string + " \"" + concept_name + "\""
        elif function_name == 'map_number':
            text_string = "{} &#8594 ({},{})".format(arg_row['mapped_number'], arg_row['to_concept_vocabulary_id'], arg_row['to_concept_code'])
            text_string = text_string + " \"" + concept_name + "\""
        elif function_name == 'not_null_number':
            value_flag='x?x'
            if arg_row['mapped_number'] == -1.0:
                value_flag = 'null'
            elif arg_row['mapped_number'] == 0.0:
                value_flag = '0'
            elif arg_row['mapped_number'] > 0.0:
                value_flag = '>0'
            text_string = "{} &#8594 ({},{})".format(value_flag, arg_row['to_concept_vocabulary_id'], arg_row['to_concept_code'])
            text_string = text_string + " \"" + concept_name + "\""
        elif function_name == 'linear_equation':
            text_string = "factor {} shift:{}".format(arg_row['transform_factor'], arg_row['transform_shift'])

        text_list.append(text_string)

    return text_list

def _print_header(name_keys, study_mappings, column_keys, show_detail, html, key_display_names):
    """ header 
        Param name_keys
        Param study_mappings,  dictionary by study_id of dictionaries by (vocabulary_id, concpet_code) pairs
        Param column_keys
        Param show_detail, a boolean flag for detail display
    """

    if html:
        #print("<tr bgcolor=\"#EEEEE0\" width=\"100%\"><td colspan=100>&nbsp</td></tr>")

        print("<tr bgcolor=\"#EEEEE0\">")

    for nkey in name_keys:
        #print(f"<td>{nkey[0]: <{nkey[1]}}</td>", end=nkey[2])
        print(f"<td><b>{(key_display_names[nkey[0]])}:</b></td>", end=nkey[2])

    for study_id in study_mappings.keys():
        for ckey in column_keys:
            if show_detail and ckey[0] == 'function_name':
                if html:
                    print("<td> <b>", end="")
                arbitrary_concept_key = next(iter(study_mappings[study_id].keys()))
                study_name = study_mappings[study_id][arbitrary_concept_key]['study_name']
                if html:
                    print('Function', end=ckey[2])
                else:
                    print(f"{'function': <{ckey[1]}}", end=ckey[2])
                if html:
                    print("</b></td >")

            if ckey[0] == 'from_column':
                if html:
                    print("<td ><b>", end="")
                arbitrary_concept_key = next(iter(study_mappings[study_id].keys()))
                study_name = study_mappings[study_id][arbitrary_concept_key]['study_name']
                if html:
                    print('Column', end=ckey[2])
                else:
                    print(f"{'column': <{ckey[1]}}", end=ckey[2])
                if html:
                    print("</b></td >")

            if ckey[0] == 'from_table':
                if html:
                    print("<td ><b>", end="")
                arbitrary_concept_key = next(iter(study_mappings[study_id].keys()))
                study_name = study_mappings[study_id][arbitrary_concept_key]['study_name']
                #print(f"{study_name +  ' ' + ckey[0]: <{ckey[1]}}", end=ckey[2])
                if html:
                    print(study_name +  ' ' + 'Table', end=ckey[2])
                else:
                    print(f"{study_name +  ' ' + 'table': <{ckey[1]}}", end=ckey[2])
                if html:
                    print("</b></td >")

            if ckey[0] != 'function_name' and ckey[0] != 'from_column' and ckey[0] != 'from_table':
                if html:
                    print("<td >", end="")
                arbitrary_concept_key = next(iter(study_mappings[study_id].keys()))
                study_name = study_mappings[study_id][arbitrary_concept_key]['study_name']
                if html:
                    print(f"{study_name +  ' ' + ckey[0]: <{ckey[1]}}", end=ckey[2])
                else:
                    print(f"{study_name +  ' ' + ckey[0]: <{ckey[1]}}", end=ckey[2])
                if html:
                    print("</b></td >")

            #print(ckey[0], end=ckey[2])
            #print(study_name, end=ckey[2])

    if html:
        print("</tr>\n")
    print('')

def _get_study_details(study_id, table_name, cur):
    x = BasePerson.factory_on_id(study_id)
    date_col =   x.get_date_column_for_table(table_name)
    if date_col == BASE_DATE:
        return None
    else:
        return date_col

def _get_arguments(study_mappings, column_keys, concept_key, show_detail, cur, dict_cur, html):
    arguments_text={}
    for study_id in study_mappings.keys():
        # COMMENTS, UNITS, Etc.
        arguments_text[study_id] = []
        if show_detail and concept_key in study_mappings[study_id]:
            stuff = study_mappings[study_id][concept_key]
            detail = '\n<!-- arguments text -->\n'
    
            # These are actually unused and so clutter
            if stuff['comment']:
                detail = ' comment:"' + stuff['comment'] + '"' 
                arguments_text[study_id].append(detail)
            #if stuff['has_date']: # note the value is boolean. It may become a column name...
                # worse, it *is* a column at the moment, but it's name is buried in Person.py. SMH TODO
    
            study_detail = _get_study_details(study_id, stuff['from_table'], cur)
            if study_detail: 
                detail = ' has date:' +  study_detail
                arguments_text[study_id].append(detail)
    
            if stuff['units']:
                detail = ' units:' + stuff['units']
                arguments_text[study_id].append(detail)
    
            if 'from_where_column' in stuff and stuff['from_where_column']:
                detail = ' where: ' + stuff['from_where_column']
            if 'from_where_clause' in stuff and stuff['from_where_clause']:
                detail = detail +  '=' + stuff['from_where_clause']
            if 'from_where_clause' in stuff and stuff['from_where_clause']:
                arguments_text[study_id].append(detail)
    
            #if len(detail) > 0:
# else:
 #arguments_text[study_id].append("(just defaults)")
        
    
        # MAPPING DETAIL
        if show_detail and concept_key in study_mappings[study_id]:
            #study_arguments_text = create_arguments_text(study_id, concept_key[0], concept_key[1], 
            study_arguments_text = create_arguments_html(study_id, concept_key[0], concept_key[1], 
                        study_mappings[study_id][concept_key]['from_table'], 
                        study_mappings[study_id][concept_key]['from_column'], 
                        study_mappings[study_id][concept_key]['function_name'], 
                        dict_cur)
            arguments_text[study_id].append(study_arguments_text)

    return arguments_text

def _get_main_row(study_mappings, column_keys, concept_key, show_detail, cur, dict_cur, html):
    """ Assembles the main row as well as the arguments involved, if called for by the show_detail flag.
        Param study_mappings,  dictionary by study_id of dictionaries by (vocabulary_id, concpet_code) pairs
        Param column_keys
        Param concept_key
        Param show_detail, a boolean flag for detail display
        Param cur, a django cursor
        Param dict_cur, a django dictionary cursor
    """

    main_text={}
    for study_id in study_mappings.keys():
        main_text[study_id]=""
        # MAIN ROW
        if (concept_key in study_mappings[study_id].keys()):
            # IMPORTED from study via config in study_to_ohdsi_mapping
            stuff = study_mappings[study_id][concept_key]
            for ckey in column_keys:
                study_main_text=""
                the_value =  stuff[ckey[0]]
                if ckey[0] == 'from_table':
                    if len(the_value.split('.')) > 1:
                        the_value = the_value.split('.')[1]
                shortened_value =  the_value[0:ckey[1]-1]
                if ckey[0] != 'function_name':
                    if html:
                        study_main_text = study_main_text + "<td>"
                    study_main_text = study_main_text +  shortened_value # f'{shortened_value: <{ckey[1]}}' 
                    if html:
                        study_main_text = study_main_text + "</td>"
                elif show_detail:
                    if html:
                        study_main_text = study_main_text + "<td>"
                    study_main_text = study_main_text + shortened_value #f'{shortened_value: <{ckey[1]}}'
                    if html:
                        study_main_text = study_main_text + "</td>"
                main_text[study_id] = main_text[study_id] + study_main_text
        else:
            # DERIVED, not mapped in study_to_ohdsi_mapping
            for ckey in column_keys:
                study_main_text=""
                if ckey[0] != 'function_name':
                    if is_derived_variable(study_id, concept_key[0], concept_key[1], cur) :
                        if html:
                            study_main_text = study_main_text + "<td>"
                        study_main_text = study_main_text + f"{'*derived*': <{ckey[1]}}"
                        if html:
                            study_main_text = study_main_text + "</td>"
                    else:
                        if html:
                            study_main_text = study_main_text + "<td>"
                        study_main_text = study_main_text + f"{'NA': <{ckey[1]}}"
                        if html:
                            study_main_text = study_main_text + "</td>"
                elif show_detail:
                    if is_derived_variable(study_id, concept_key[0], concept_key[1], cur) :
                        if html:
                            study_main_text = study_main_text + "<td>"
                        study_main_text = study_main_text + f"{'*derived*': <{ckey[1]}}"
                        if html:
                            study_main_text = study_main_text + "</td>"
                    else:
                        if html:
                            study_main_text = study_main_text + "<td>"
                        study_main_text = study_main_text + f"{'NA': <{ckey[1]}}"
                        if html:
                            study_main_text = study_main_text + "</td>"
                main_text[study_id] = main_text[study_id] + study_main_text
    return main_text


def _print_args_html(arguments_text, study_mappings, html):
    """
        Param arguments_text
        Param show_detail, a boolean flag for detail display
        Param study_mappings,  dictionary by study_id of dictionaries by (vocabulary_id, concpet_code) pairs
    """
    study_count=0
    for study_id in study_mappings.keys(): 
        study_count=study_count + 1
        color_tag = ""
        if study_count % 2 == 1:
            color_tag=" bgcolor=\"#F0F0F0\" "
        print(f"<td colspan=3 valign=\"top\" {color_tag} style=\"border:1px solid black;\"><table>")
        if  study_id in arguments_text.keys():
            combined_text=""
            for bit_of_text in arguments_text[study_id]:
                print(f"<tr><td width=\"100%\" valign=\"top\">{bit_of_text: <{48}} </td></tr>", end='')
        print("</td></table>")

def _print_args_text(arguments_text, study_mappings, html):
    """
  may still not be rigth for text as that code may yet be abandonded
        Param arguments_text
        Param show_detail, a boolean flag for detail display
        Param study_mappings,  dictionary by study_id of dictionaries by (vocabulary_id, concpet_code) pairs
    """
    text_row_index=0
    max_rows=0
    for study_id in arguments_text.keys():
        max_rows = max(max_rows, len(arguments_text[study_id]))

    study_count=0
    while (text_row_index < max_rows):
        for study_id in study_mappings.keys(): 
            study_count=study_count + 1
            if study_id in arguments_text.keys() and len(arguments_text[study_id]) > text_row_index:
                if study_count % 2 == 0:
                    print(f"<td colspan=3 valign=\"top\">{arguments_text[study_id][text_row_index]: <{48}} </td>", end='')
                else:
                    print(f"<td colspan=3 valign=\"top\" bgcolor=\"#F0F0F0\">{arguments_text[study_id][text_row_index]: <{48}} </td>", end='')
        text_row_index  = text_row_index  + 1

def _get_detail(study_export_mappings, concept_key):
    """ does it for the first study found only """

    detail_string="\n <!-- args detail -->\n"
    for study_id in study_export_mappings.keys():
        detail_string = detail_string + "<td colspan=4 valign=\"top\" style=\"border:1px solid black;\">"
        detail_string = detail_string + "<table width=\"100%\" border=0 valign=\"top\">"
        color_tag=" bgcolor=\"#FFFFF0\" "
        detail_string = detail_string + "<tr><td valign=\"top\" width=\"100%\" " + color_tag + ">" 
        detail_string = detail_string +  "<b>Export Detail:</b></td></td>\n"
        for detail_row in study_export_mappings[concept_key]:
            detail_string = detail_string + "<tr><td valign=\"top\" width=\"100%\" " + color_tag + " style=\"white-space:nowrap\" >" 
            if detail_row['function_name'] == 'map_concept_id':
                detail_string = detail_string + "{}  ({}, {}) \"{}\" &#8594  {}".format(
                    detail_row['function_name'], 
                    detail_row['vocabulary_id'], 
                    detail_row['concept_code'], 
                    detail_row['concept_name'], 
                    detail_row['rank'])
            elif detail_row['function_name'] == 'identity_number' or detail_row['function_name'] == 'identity_string':
                detail_string = detail_string +  detail_row['function_name']
            elif detail_row['function_name'] == 'ranges_to_rank_asc' or detail_row['function_name'] == 'ranges_to_rank_desc':
                detail_string = detail_string +  "{} {} {}".format(detail_row['function_name'], detail_row['rank'], detail_row['value_limit'])  
            else:
                detail_string = detail_string + str(detail_row)
            detail_string = detail_string + "</td></tr>  "
        detail_string = detail_string + "</table></td>\n"
        return detail_string

def _print_cfg(concept_keys, study_mappings, study_export_mappings, name_map, cfg, cur, show_detail, show_unused, dict_cur, html, key_display_names):
    """ Uses a pair of lists of triples as a configuration of what to print.
        Param concept_keys,  describes items common to all studies: basically the concept
        Param study_mappings,  dictionary by study_id of dictionaries by (vocabulary_id, concpet_code) pairs 
        Param name_map
        Param cfg   a pair of lists: the first is a list of tuples, one for each OMOP variable. 
            The second is  a list of tuples, one for each study variable. The tuples are the same for both: the first
            item is the variable name and the second is its display width.
        Param cur, a django cursor
        Param show_detail, a boolean flag for detail display
        Param show_unused, a boolean flag for showing unexported concepts
        Param dict_cur, a django dictionary cursor

        The triples have a value for each of (key, width, separator).
        This level of configuration means you can use this for CSV creation as well as a visual text table.
    """

    (name_keys, column_keys) = cfg

    print("<!-- start of print_cfg -->")
    print("<table  border=0 valign=\"top\">") 

    # extracted data
    exported_keys = set()

    concept_count=-1
    for concept_key in name_map.keys():
        concept_count = concept_count + 1

        if (concept_count % 1 == 0):
            _print_header(name_keys, study_mappings, column_keys, show_detail, html, key_display_names)
            # TODO make a scrolling page under a fixed header

        print("<tr bgcolor=\"#EEEEE0\" >")
        exported_keys.add(concept_key)
        if (concept_key in name_map.keys()):
            for nkey in name_keys:
                shortened_value = name_map[concept_key][nkey[0]][0:nkey[1]-1]
                print("<td>", end='')
                print(shortened_value)
                print("</td>")

            main_row_text = _get_main_row(study_mappings, column_keys, concept_key, show_detail, cur, dict_cur, html)
            for mrt in main_row_text:
                print(main_row_text[mrt])
            print("</tr>")

            print("<tr>") 
            detail_text = _get_detail(study_export_mappings, concept_key)
            print(detail_text)

            arguments_text = _get_arguments(study_mappings, column_keys, concept_key, show_detail, cur, dict_cur, html)
            _print_args_html(arguments_text, study_mappings, html)
        print("</tr>")
            
               
    if show_unused:
        # non-extracted data, so no entries in name-map here, and no short-names to be found.
        # name, width, separator
        non_exported_keys = concept_keys - exported_keys
        for concept_key in non_exported_keys:
            concept_count = concept_count + 1
            if (concept_count % 1 == 0):
                _print_header(name_keys, study_mappings, column_keys, show_detail, html, key_display_names)
            print("<tr bgcolor=\"#EEEEE0\" >")
            for nkey in name_keys:
                if (nkey[0] == 'short_name'):
                    print(f'<td>{"n/a": <{nkey[1]}}</td>')
                elif (nkey[0] == 'vocabulary_id'):
                    print(f'<td>{concept_key[0]: <{nkey[1]}}</td>')
                elif (nkey[0] == 'concept_code'):
                    print(f'<td>{concept_key[1]: <{nkey[1]}}</td>')
                elif (nkey[0] == 'concept_name'):
                    concept_name = _lookup_concept_name(concept_key[0], concept_key[1], cur);
                    shortened_value = concept_name[0:nkey[1]-1]
                    print(f'<td>{shortened_value: <{nkey[1]}}</td>')

            main_text = _get_main_row(study_mappings, column_keys, concept_key, show_detail, cur, dict_cur, html)
            for mrt in main_row_text:
                print(main_row_text[mrt])
            print("</tr>")

            print("<tr>") 
            ## no detail since not output ##
            print("<td colspan=4 bgcolor=\"#FFFFF0\"  valign=\"top\" style=\"border:1px solid black;\" >(not exported)</td>")
            arguments_text = _get_arguments(study_mappings, column_keys, concept_key, show_detail, cur, dict_cur, html)
            _print_args_html(arguments_text, study_mappings, html)
            print("</tr>")
    if html:
        print("</table>") 


def _display_study_calculations(study_id, extract_study_id, skip_not_extracted, cur, html):
    print("")
    study_name = _lookup_study_name(study_id, cur)
    if html:
        print(f"<h2>{study_name} {study_id} Calculations </h2>")
    else:
        print(study_name, study_id)
        print("==================="[0:len(study_name) + 3])
    study_calcs = get_study_calculations_map(study_id, extract_study_id, cur)
#    stmt = """ SELECT distinct  o.to_vocabulary_id, o.to_concept_code, o.function_name, c.short_name, sequence

    # This fails to show inputs that are not imported. ??? TODO

    if study_calcs:
        if html:
            print("<table border=1>")
        for (v,c) in study_calcs:
            (der_vocab_id, der_concept_code, function_name, short_name, sequence) = study_calcs[(v,c)]
            if not skip_not_extracted or short_name :
                der_concept_name = _lookup_concept_name(der_vocab_id, der_concept_code, cur)
                short_name = "\"" + short_name + "\""
                pair = "(" + der_vocab_id + ", " + der_concept_code + ")"
                calc_args = get_calculation_arguments(study_id, extract_study_id, der_vocab_id, der_concept_code, cur)
                if html:
                    print(f"<tr><td colspan=5><b>{short_name} {pair} \"{der_concept_name}\" func:{function_name} </b></td</tr>")
                if calc_args and len(calc_args) > 0:
                    if html:
                        print(f"<tr><th>Concept</th> <th>Name</th><th>Abbreviation</th><th>table</th><th>column</th></tr>") # TODO
                    else:
                        print(f"{short_name:<10} {pair:<21} {der_concept_name:<25} func:{function_name:<20}")
                    for (vocab_id, concept_code, concept_name, short_name, name, order, val) in calc_args:
                        #concept_name='';
                        if (vocab_id == 'dual'): # see #135 to see why I'm mixing concept_code and concept_id. TODO
                            concept_name = _lookup_concept_name_by_id(concept_code, cur)
                        else:
                            concept_name = _lookup_concept_name(vocab_id, concept_code, cur)
                        pair = "(" + vocab_id + ", " + concept_code + ")"
                        if short_name:
                            short_name = "\"" + short_name + "\""
                        else:
                            short_name = '(not extracted)'
                        parts = _fetch_study_source_location_by_concept(study_id, vocab_id, concept_code, cur)

                        if parts and len(parts) > 0:
                            (table, column, func) = parts
                            if html:
                                print(f"<tr>    <td>{pair}</td> <td>{concept_name[0:29]}</td> <td>{short_name:}</td> <td>{table:<30}</td> <td>{column:<15}</td></tr> ") # {func:<15} <br>")
                            else:
                                print(f"    {pair:<25} {concept_name[0:29]:<30} {short_name:<20} {table:<30} {column:<15} ") # {func:<15}")
                        else:
                            # selects from the dual table won't appear in study_to_ohdsi_mapping, as those above do
                            if html:
                                print(f"<tr>    <td>{pair}</td> <td>{concept_name[0:29]}</td> <td>{short_name}</td> <td>{name}</td> <td>{val}</td> </tr>")
                            else:
                                print(f"    {pair:<25} {concept_name[0:29]:<30} {short_name:<20} {name} {val}")
                else:
                    if html:
                        print(f"<tr><td colspan=5>no arguments for function {function_name}</td></tr>")
                    else:
                        print(f"no arguments for function {function_name})")
        if html:
            print("</table>")


def _display_not_mapped(concept_keys, maps, name_map, cur):
    for concept_key in concept_keys:
        if (not concept_key in name_map.keys()):
            vocab_id = concept_key[0]
            concept_code = concept_key[1]
            calculation_info = _lookup_concept_in_calculation(vocab_id, concept_code, cur)
            if concept_code and not calculation_info:
                concept_name = _lookup_concept_name(vocab_id, concept_code, cur)
                print('not exported   ', end='') 
                print(f'{vocab_id: <10}', end='') 
                print(f'{concept_code: <20}', end='')
                print(concept_name)

def _display_study_fraction():
    print('')
    for study_id in maps.keys():
        map_info = maps[study_id]
        first_key = next(iter(map_info.keys()))
        study_name = map_info[first_key]['study_name']
        
        print(f'study {study_id:>2}, {study_name:<12} has {study_var_counts[study_id]}  of {len(concept_keys)}, ', end='')
        print(f' {study_var_counts[study_id]/len(concept_keys):.1%} ')


def _display_grid(concept_keys, maps, name_map) :

    # header
    print(f"{'short_name':<15}", end='')
    print(f"{'vocab_id': <10}", end='')
    print(f"{'concept_code':<15}", end='')
    print(f"{'long_name':<30}", end='')
    #print(f"{'concept_name': <22}", end='')
    study_var_counts = {}
    for study_id in maps.keys():
        print(f"{study_id: >3}",end='')
        study_var_counts[study_id]=0
    print('')

    lines={}
    # data
    for concept_key in concept_keys:
        if (concept_key in name_map.keys()):
            line=""
            vocab_id = concept_key[0]
            concept_code = concept_key[1]
            short_name = name_map[(vocab_id, concept_code)]["short_name"]

            line = line + f'{short_name: <15}'
            line = line + f'{vocab_id: <10}'
            line = line + f'{concept_code: <15}'
    
            long_name = name_map[(vocab_id, concept_code)]["long_name"][:28]
            line = line + f'{long_name: <30}'
    
            for study_id in maps.keys():
                if concept_key in maps[study_id]:
                    line = line + "  x"
                    study_var_counts[study_id] = study_var_counts[study_id]  + 1
                else:
                    line = line + "   "
            lines[short_name] = line

    # display
    #for key in list(lines.keys()).sort():
    keylist = list(lines.keys())
    keylist.sort(key=lambda s: s.lower())
    for key in keylist:
        print(lines[key])
    
def _display_study_metadata(study_id, dict_cur, html):
    """
        Text-style report for study-level metadata kept in the study table.   
        param study_id
        param dict_cur
    """

    stmt = """
            SELECT  study_name, person_id_range_start, person_id_range_end, id_field_name, sex_table_name, sex_column_name, race_table_name, race_column_name, person_id_select, person_details_select
            FROM study
            WHERE study_id = %s
            ORDER BY study_id;
            """
    dict_cur.execute(stmt, [study_id])
    cfg_rows = dict_cur.fetchall()
    for crow in cfg_rows: # only expect a single row 
        if html:
            print(f"<h2>{crow['study_name']} Study ID details</h2>")
            print("<table border=1>")
            print("<tr><th>Name</th><th>ID field</th><th>ID select</th><th>ID details</th></tr>")
            print(f"<tr><td>{crow['study_name']}</td>")
            print(f"<td>{crow['id_field_name']}</td>")
            print(f"<td>{crow['person_id_select']}</td>")
            print(f"<td>{crow['person_details_select']}</td></tr>")
            print("</table>")
        else:
            print("")
            print(f"name: {crow['study_name']}")
            print(f"id field:   {crow['id_field_name']}")
            print(f"id select:  {crow['person_id_select']}")
            print(f"id details: {crow['person_details_select']}")

    stmt = """ SELECT file_path from study_files where study_id = %s """
    dict_cur.execute(stmt, [study_id])
    cfg_rows = dict_cur.fetchall()
    for crow in cfg_rows:
        if html:
            print(f"file: {crow['file_path']}<br>")
        else:
            print(f"file:{crow['file_path']}")
    

    

# report type can be one of 'CSV', 'TXT', or 'GRID'
def main(report_type, extract_study_id, detail, unused) :

    db_name=os.environ.get('PGDATABASE')
    user_name=os.environ.get('PGUSER')

    con = psycopg2.connect(database=db_name, user=user_name) 
    con.autocommit=True;
    cur = con.cursor()
    dict_cur = con.cursor(cursor_factory=RealDictCursor)

    studies = ('21','22','23','24'); # <<--- TOOD why have this AND the "not in" above??

    try:
        (study_mappings, super_key_set) = _get_study_mappings_by_extract_study(extract_study_id, cur, dict_cur)
        export_study_mappings = _get_categorization_parameters_for_extract_study(extract_study_id, dict_cur)
        name_map = None
        if extract_study_id == 'None': 
            name_map = _fetch_extracted_names(None, cur)
        else:
            name_map = _fetch_extracted_names(extract_study_id, cur)
 
        if report_type == 'GRID':
            _display_grid(super_key_set, study_mappings, name_map)
            print('')
            _display_not_mapped(super_key_set, study_mappings, name_map, cur)
            print('')
        elif report_type == 'CSV':
            csv_cfg = (
                [ ('short_name', 0, ','), ('vocabulary_id', 0, ','), ('concept_code', 0, ','), ('concept_name', 0, '') ],   
                [ ('from_table',0, ','), ('from_column', 0, ','), ('function_name', 0, ',') ])
            _print_cfg(super_key_set, study_mappings, export_study_mappings, name_map, csv_cfg, cur, detail == 'True', unused == 'True', dict_cur, False, {})
        elif report_type == 'TXT':
            print("  HeartData/cfg_across_studies_cfg  ", extract_study_id, report_type)
            print("")
            txt_cfg = (
                [ ('short_name', 11, ''), ('vocabulary_id', 14, ''), ('concept_code', 13, '') , ('concept_name', 20, '') ],    
                [ ('from_table', 20, ''), ('from_column', 17, ''),  ('function_name', 12, '') ])
            _print_cfg(super_key_set, study_mappings, export_study_mappings, name_map, txt_cfg, cur, detail == 'True', unused == 'True', dict_cur, False, {})
            print('')
            print("Derived variables extract in this export configuration:")
            for study_id in studies:
                _display_study_calculations(study_id, extract_study_id, True, cur, False)
                _display_study_metadata(study_id, dict_cur, False)
        elif report_type == 'HTML':
            print("<html><head><title>Report</title></head><body>")
            print("<h2>  HeartData/cfg_across_studies_cfg  ", extract_study_id, report_type, "</h2>")
            key_display_names  = { 'short_name':'Short Name', 
                                    'vocabulary_id':'Vocabulary',
                                    'concept_code':'Concept', 
                                    'concept_name':'Name',
                                    'from_table':'Table', 
                                    'from_column':'Column', 
                                    'function_name':'Function' }
            txt_cfg = (
                [ ('short_name', 11, ''), ('vocabulary_id', 14, ''), ('concept_code', 13, '') , ('concept_name', 20, '') ],     # (once) name_keys
                [ ('from_table', 20, ''), ('from_column', 17, ''),  ('function_name', 12, '') ])                                # (per-study) column_keys
            _print_cfg(super_key_set, study_mappings, export_study_mappings, name_map, txt_cfg, cur, detail == 'True', unused == 'True', dict_cur, True, key_display_names)
            print('')
            print("<p>Derived variables extract in this export configuration:")
            for study_id in studies:
                _display_study_calculations(study_id, extract_study_id, True, cur, True)
                print("<p>")
                _display_study_metadata(study_id, dict_cur, True)

            print("</body></html>")


        con.close()
    
    except Exception as ex:
        logger.error(ex)
        con.close()
        raise ex
    

if __name__ == '__main__':
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)

