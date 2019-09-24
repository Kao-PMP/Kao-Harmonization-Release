#!/bin/bash

# show HTML formatted (barely) report on import mappings

if ((  $# < 1 )) ; then
    echo ""
    echo "usage: show_concept_usage.sh study_id"
    echo ""
    exit
fi

STUDY_ID=$1

        ###m.from_where_column, m.from_where_clause, \

echo "SELECT s.study_name as study, m.from_table,  m.from_column, m.function_name as fn, \
		m.vocabulary_id as vocab, m.concept_code as code, \
        substring(c.concept_name, 1, 10) as concept, \
        a.mapped_string as s , a.mapped_number as n , a.to_concept_vocabulary_id as vocab, a.to_concept_code as code, \
        substring(c2.concept_name, 1, 10) as concept, \
        a.transform_factor as factor, a.transform_shift as shift \
      FROM study_to_ohdsi_mapping m, study_mapping_arguments a, study s, concept c, concept c2 \
      WHERE m.study_id = s.study_id \
        and m.vocabulary_id = c.vocabulary_id \
        and m.concept_code = c.concept_code \
		and m.study_id = $STUDY_ID \
        and a.study_id = m.study_id \
        and a.from_table = m.from_table \
        and a.from_column = m.from_column \
        and a.function_name != 'identity' \
        and a.to_concept_vocabulary_id = c2.vocabulary_id \
        and a.to_concept_code = c2.concept_code \
      ORDER by study_name, from_table, from_column;" | psql

echo "SELECT s.study_name as study, m.from_table,  m.from_column, m.function_name, \
		m.vocabulary_id, m.concept_code, c.concept_name, m.from_where_column as where_col, m.from_where_clause  as where_val\
      FROM study_to_ohdsi_mapping m, study s, concept c \
      WHERE m.study_id = s.study_id \
        and m.vocabulary_id = c.vocabulary_id \
        and m.concept_code = c.concept_code \
		and m.study_id = $STUDY_ID \
        and m.function_name = 'identity' \
      ORDER by study_name, from_table, from_column;" | psql


