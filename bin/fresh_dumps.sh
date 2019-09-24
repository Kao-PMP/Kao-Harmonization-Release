#!/usr/bin/env bash

DB=$HEART_DATABASE

echo "BACKING UP $DB"

TABLES=(\
vocabulary_concept \
table_column  \
extract_study \
study \
study_files \
study_mapping_arguments \
study_to_ohdsi_mapping \
mapping_function \
ohdsi_calculation_function \
ohdsi_calculation_argument \
categorization_function_metadata \
categorization_function_parameters \
categorization_function_qualifiers \
categorization_function_table \
events_mapping \
categorization_functions \
auth_group_id_seq \ 
auth_group_permissions_id_seq   \
auth_permission_id_seq           \ 
auth_user_groups_id_seq           \
auth_user_id_seq                  \
auth_user_user_permissions_id_seq \
django_admin_log_id_seq           \
django_content_type_id_seq        \
django_migrations_id_seq          \
mapping_function_id_seq           \
study_mapping_arguments_id_seq    \
study_to_ohdsi_mapping_id_seq     \
table_column_table_column_id_seq   )

for table in ${TABLES[@]}; do
    echo $table
    pg_dump --no-owner -t $table $DB > $table.dump
done
