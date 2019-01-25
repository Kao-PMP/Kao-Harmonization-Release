#!/usr/bin/env bash

# load the mappings data

DBNAME=$1
BACKUPS_DIR=../backups
set -e 
set -o pipefail 

echo "drop table study;" | psql $DBNAME
echo "drop table study_files;" | psql $DBNAME
echo "drop table extract_study;" | psql $DBNAME
echo "drop table vocabulary_concepts;" | psql $DBNAME
echo "drop table table_column;" | psql $DBNAME
echo "drop table mapping_function;" | psql $DBNAME

echo "drop table study_to_ohdsi_mapping;" | psql $DBNAME

echo "drop table ohdsi_calculation_function;" | psql $DBNAME
echo "drop table ohdsi_calculation_argument;" | psql $DBNAME

echo "drop table categorization_function_metadata;" | psql $DBNAME
echo "drop table categorization_function_parameters;" | psql $DBNAME
echo "drop table categorization_function_qualifiers;" | psql $DBNAME
echo "drop table categorization_function_table;" | psql $DBNAME

echo "drop table events_mapping;" | psql $DBNAME


echo "study"
psql $DBNAME < $BACKUPS_DIR/study.dump

echo "study_files"
psql $DBNAME < $BACKUPS_DIR/study_files.dump

echo "extract_study"
psql $DBNAME < $BACKUPS_DIR/extract_study.dump

echo "vocabulary_concept"
psql $DBNAME < $BACKUPS_DIR/vocabulary_concept.dump

echo "table_column"
psql $DBNAME < $BACKUPS_DIR/table_column.dump

echo "mapping_function"
psql $DBNAME < $BACKUPS_DIR/mapping_function.dump

echo "study_to_ohdsi_mapping"
psql $DBNAME < $BACKUPS_DIR/study_to_ohdsi_mapping.dump
echo "ohdsi_calculation_function"
psql $DBNAME < $BACKUPS_DIR/ohdsi_calculation_function.dump
echo "ohdsi_calculation_argument"
psql $DBNAME < $BACKUPS_DIR/ohdsi_calculation_argument.dump

echo "categorization_function_meta"
psql $DBNAME < $BACKUPS_DIR/categorization_function_metadata.dump
echo "categorization_function_parameters"
psql $DBNAME < $BACKUPS_DIR/categorization_function_parameters.dump
echo "categorization_function_qualifiers"
psql $DBNAME < $BACKUPS_DIR/categorization_function_qualifiers.dump
echo "categorization_function_table"
psql $DBNAME < $BACKUPS_DIR/categorization_function_table.dump
echo "categorization_functions"
psql $DBNAME < $BACKUPS_DIR/categorization_functions.dump

echo "events_mapping"
psql $DBNAME < $BACKUPS_DIR/events_mapping.dump
