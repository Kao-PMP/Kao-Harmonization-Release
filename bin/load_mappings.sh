#!/usr/bin/env bash

# load the mappings data

DBNAME=$1
BACKUPS_DIR=../backups
SQL_DIR=../sql
BIN_DIR=../bin
set -e 
set -o pipefail 

SEQS=(auth_group_id_seq \
auth_group_id_seq \
auth_group_permissions_id_seq   \
auth_permission_id_seq           \ 
auth_user_groups_id_seq           \
auth_user_id_seq                  \
auth_user_user_permissions_id_seq \
django_admin_log_id_seq           \
django_content_type_id_seq        \
django_migrations_id_seq          \
study_mapping_arguments_id_seq    )

#don't need to create these, but drop
OTHER_SEQS=(mapping_function_id_seq  \        
study_to_ohdsi_mapping_id_seq     \
table_column_table_column_id_seq    )

TABLES=(\
vocabulary_concept \
table_column \
categorization_function_metadata \
categorization_function_parameters \
categorization_function_qualifiers \
categorization_function_table \
categorization_functions \
events_mapping \
extract_study \
mapping_function \
ohdsi_calculation_function \
ohdsi_calculation_argument \
study \
study_files \
study_mapping_arguments \
study_to_ohdsi_mapping \
table_column \
)

echo ""
echo "START DROPPING"
for seq in ${SEQS[@]}; do
    echo "drop seq $seq"
    echo "drop sequence $seq cascade;" |  psql $DBNAME > /dev/null
done

for seq in ${OTHER_SEQS[@]}; do
    echo "drop other seq $seq"
    echo "drop sequence $seq cascade;" |  psql $DBNAME > /dev/null
done

for table in ${TABLES[@]}; do
    echo "drop table $table"
    echo "drop table $table cascade;" |  psql $DBNAME > /dev/null
done

echo ""
echo "START VERIFYING"
set +e
for table in ${TABLES[@]}; do
    echo "\d $table" | psql &> /dev/null
    if [ $? ] ; then
        echo "verify $table is dropped"
    else    
        echo " $? table $table NOT dropped!"
        exit
    fi 
done
set -e

echo ""
echo "START LOADING SEQS"
for seq in ${SEQS[@]}; do
    echo "load seq $seq"
    psql $DBNAME < $BACKUPS_DIR/$seq.dump > /dev/null
done

echo ""
echo "START LOADING TABLES"
for table in ${TABLES[@]}; do
    echo "load table $table"
    psql $DBNAME < $BACKUPS_DIR/$table.dump > /dev/null
done

# VERIFY: Using the -c flag makes it so we get an error return if the table isn't there to describe. 
# The -e set at the top of the script makes it so the script then fails with error, which will be
# detected higher up.
for table in ${TABLES[@]}; do
    psql -c "\d $table"  &> verify.$table.log
    echo "VERIFY $table $?"
done


# BTW, load the concepts
echo "CONCEPTS"
    psql  < $SQL_DIR/concept.sql
