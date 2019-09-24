#!/usr/bin/env bash

# show counts of things by study_id

echo "STUDY MAPPING"
echo "select count(*), study_id from study_to_ohdsi_mapping group by study_id order by study_id;" | psql
echo "select count(*), study_id from study_mapping_arguments group by study_id order by study_id;" | psql

echo "CALCULATION"
echo "select count(*), study_id from ohdsi_calculation_function group by study_id order by study_id;" | psql
echo "select count(*), study_id from ohdsi_calculation_argument group by study_id order by study_id;" | psql

echo "CATEGORIZATION"
echo "select count(*), extract_study_id from categorization_function_metadata group by extract_study_id order by extract_study_id;  " | psql
echo "select count(*), extract_study_id from categorization_function_parameters group by extract_study_id order by extract_study_id; " | psql

