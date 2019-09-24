#!/usr/bin/env bash

# copy_study_config1.sh <study_id> <new_id>
#
# copies a study mapping configuration from one id to another for the following tables:
#   study
#   study_files
#   study_to_ohdsi_mapping
#   study_mapping_arguments
#    events_mapping
#   ohdsi_calculation_function
#   ohdsi_calculation_argument


function usage() {
    echo "copy_extract.sh <_study_id> <new_id>"
}

if [[ $# -ne 2 ]]; then
    usage
    exit 0
fi

STUDY_ID=$1
NEW_STUDY_ID=$2

if (( STUDY_ID == $NEW_STUDY_ID ))
then
    echo "must have different study ids"
    exit 1
fi

echo "delete from study_mapping_arguments where study_id = $NEW_STUDY_ID;" | psql
echo "status $?"
echo "delete from study_to_ohdsi_mapping where study_id = $NEW_STUDY_ID;" | psql
echo "status $?"
echo "delete from ohdsi_calculation_argument where study_id = $NEW_STUDY_ID;" | psql
echo "status $?"
echo "delete from ohdsi_calculation_function where study_id = $NEW_STUDY_ID;" | psql
echo "status $?"
echo "delete from events_mapping where study_id = $NEW_STUDY_ID;" | psql
echo "status $?"
echo "delete from study_files where study_id = $NEW_STUDY_ID;" | psql
echo "status $?"
echo "delete from study where study_id = $NEW_STUDY_ID;" | psql
echo "status $?"
echo ""
echo ""
echo ""

echo "STUDY"
SQL="insert into study select $NEW_STUDY_ID, concat(study_name,'-',$NEW_STUDY_ID), person_id_range_start, person_id_range_end, observation_range_start, observation_range_end,'f','f','f',id_field_name,person_id_prefix, person_id_select, person_details_select, study_class, sex_table_name, sex_column_name, sex_function_name, race_table_name, race_column_name, race_function_name from study where study_id = $STUDY_ID;"
echo $SQL | psql
echo "status $?"

echo "STUDY_FILES"
SQL="insert into study_files select $NEW_STUDY_ID, file_path from study_files where study_id = $STUDY_ID;"
echo $SQL | psql
echo "status $?"

echo "STUDY_TO_OHDSI_MAPPING $NEW_STUDY_ID"
SQL="insert into study_to_ohdsi_mapping select $NEW_STUDY_ID, from_table, from_column, function_name,vocabulary_id,concept_code, to_table, to_column, addl_value_1, addl_column_1, from_where_clause, comment, from_where_column, units, has_date, nextval('study_to_ohdsi_mapping_id_seq'::regclass)  from study_to_ohdsi_mapping where study_id = $STUDY_ID"
echo $SQL 
echo $SQL | psql
echo "status $?"

echo "STUDY_MAPPING_ARGUMENTS"
SQL="insert into study_mapping_arguments select $NEW_STUDY_ID, from_table, from_column, function_name, from_where_clause, from_where_column, mapped_string, mapped_number, mapped_concept_vocabulary_id, mapped_concept_code, transform_factor, transform_shift,id,to_concept_vocabulary_id, to_concept_code from study_mapping_arguments where study_id = $STUDY_ID;"
echo $SQL | psql
echo "status $?"

echo "OHDSI_CALCULATION_FUNCTION"
SQL="insert into ohdsi_calculation_function select $NEW_STUDY_ID, function_name, to_vocabulary_id, to_concept_code, to_table, to_column, function_order, expression, module_name from ohdsi_calculation_function where study_id = $STUDY_ID;"
echo $SQL | psql
echo "status $?"

echo "OHDSI_CALCULATION_ARGUMENT"
SQL="insert into ohdsi_calculation_argument select vocabulary_id, concept_code, $NEW_STUDY_ID, function_name, argument_order, argument_name, value_field, to_concept_code, to_vocabulary_id, from_table from ohdsi_calculation_argument where study_id = $STUDY_ID;"
echo $SQL | psql
echo "status $?"

echo "EVENTS_MAPPING"
SQL="insert into events_mapping select $NEW_STUDY_ID, from_table, from_column, to_table, to_column, value_vocabulary_id, value_concept_code, addl_column, addl_value, from_date_column, where_clause, comment from events_mapping where study_id = $STUDY_ID"
echo $SQL | psql
echo "status $?"

