#!/usr/bin/env bash

# remove_extract.sh <extract_study_id> <short_name>
#
# removes an extract configuration from one id to another for the following tables:
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
SHORT_NAME=$2

SQL="select long_name from categorization_function_metadata where extract_study_id = $EXTRACT_STUDY_ID and short_name = '$SHORT_NAME'"
LONG_NAME=$(echo $SQL | psql | tail -3 | head -1 )
echo "LONG_NAME ----$LONG_NAME---"
echo ""
echo "CATEGORIZATION_FUNCTION_PARAMETERS"
# ategorization_function_parameters_pkey" PRIMARY KEY, btree (extract_study_id, function_name, long_name, rule_id, rank)
QSQL="select *  from categorization_function_parameters where extract_study_id = $EXTRACT_STUDY_ID and long_name = '$LONG_NAME';"
echo "$QSQL" | psql
echo $?
DELETE="delete from categorization_function_parameters where extract_study_id = $EXTRACT_STUDY_ID and long_name = '$LONG_NAME';"
echo "$DELETE" | psql



#echo "CATEGORIZATION_FUNCTION_METADATA"
QSQL="select * from categorization_function_metadata where extract_study_id = $EXTRACT_STUDY_ID and short_name = '$SHORT_NAME';"
echo "$QSQL"
echo "$QSQL" | psql

DELETE="delete from categorization_function_metadata where extract_study_id = $EXTRACT_STUDY_ID and short_name = '$SHORT_NAME';"
echo "$DELETE" | psql
echo $?

