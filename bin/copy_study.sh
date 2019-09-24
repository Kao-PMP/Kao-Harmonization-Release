#!/usr/bin/env bash

# copy_extract.sh <extract_study_id> <new_id>
#
# copies an extract configuration from one id to another for the following tables:
#   extract_study
#   categorization_function_metadata
#   categorization_function_parameters
#   categorization_function_qualifiers

function usage() {
    echo "copy_extract.sh <extract_study_id> <new_id>"
}

if [[ $# -ne 2 ]]; then
    usage
    exit 0
fi

EXTRACT_STUDY_ID=$1
NEW_STUDY_ID=$2

if (( $EXTRACT_STUDY_ID == $NEW_STUDY_ID ))
then
    echo "must have different study ids"
    exit 1
fi

echo "EXTRACT_STUDY $NEW_STUDY_ID, $EXTRACT_STUDY_ID"
SQL="insert into extract_study select $NEW_STUDY_ID, study_id, name, comment from extract_study where extract_study_id = $EXTRACT_STUDY_ID;"
echo $SQL
echo $SQL | psql
echo $?

echo "CATEGORIZATION_FUNCTION_METADATA"
SQL="insert into categorization_function_metadata select $NEW_STUDY_ID, function_name, long_name, rule_id, from_vocabulary_id, from_concept_code, comment, from_table, short_name, sequence from categorization_function_metadata where extract_study_id = $EXTRACT_STUDY_ID;"
echo $SQL
echo $SQL | psql
echo $?

echo "CATEGORIZATION_FUNCTION_PARAMETERS"
SQL="insert into categorization_function_parameters select $NEW_STUDY_ID, function_name, long_name, rule_id, value_limit, rank, from_string, from_concept_id from categorization_function_parameters where extract_study_id = $EXTRACT_STUDY_ID;"
echo $SQL
echo $SQL | psql
echo $?
