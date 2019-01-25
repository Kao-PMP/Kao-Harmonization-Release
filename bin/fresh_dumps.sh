#!/usr/bin/env bash

DB=$HEART_DATABASE
echo "BACKING UP $DB"
TABLES=(\
vocabulary_concept \
table_column  \
extract_study \
study \
study_files \
study_to_ohdsi_mapping \
mapping_function \
ohdsi_calculation_function \
ohdsi_calculation_argument \
categorization_function_metadata \
categorization_function_parameters \
categorization_function_qualifiers \
categorization_function_table \
events_mapping \
categorization_functions
)
for table in ${TABLES[@]}; do
    echo $table
    pg_dump --no-owner -t $table $DB > $table.dump
done

