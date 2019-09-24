#!/usr/bin/env bash

# delete data for a study
# WARNING: destructive!

STUDY_ID=$1
echo "study $STUDY_ID"

LOWER=`echo "select person_id_range_start, person_id_range_end from  study where study_id = $STUDY_ID;" | psql | head -3 | tail -1  | awk '{print $1}'`
UPPER=`echo "select person_id_range_start, person_id_range_end from  study where study_id = $STUDY_ID;" | psql | head -3 | tail -1  | awk '{print $3'}`

echo "select count(*) from observation where person_id >= $LOWER and person_id < $UPPER;" | psql
echo "select count(*) from measurement where person_id >= $LOWER and person_id < $UPPER;" | psql

echo "study $1 lower $LOWER upper $UPPER good?"
read ANS
echo "going for it"


echo "delete from observation where person_id >= $LOWER and person_id < $UPPER;" | psql
echo "delete from measurement where person_id >= $LOWER and person_id < $UPPER;" | psql
echo "delete from visit_occurrence where person_id >= $LOWER and person_id < $UPPER;" | psql
echo "delete from procedure_occurrence where person_id >= $LOWER and person_id < $UPPER;" | psql
echo "delete from death where person_id >= $LOWER and person_id < $UPPER;" | psql
echo "delete from person where person_id >= $LOWER and person_id < $UPPER;" | psql

echo "select count(*) from observation where person_id >= $LOWER and person_id < $UPPER;" | psql
echo "select count(*) from measurement where person_id >= $LOWER and person_id < $UPPER;" | psql

