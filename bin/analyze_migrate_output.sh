#!/usr/bin/env bash

# ./analyze_migrate_output.py <file>
#
# analyze the output of migrate.py
#
# croeder October, 2017

FILE="$1"
STUDY_SCHEMA=$2
TMPFILE=/tmp/analyze_migrate_output.tmp
TMPFILE_2=/tmp/analyze_migrate_output_2.tmp
BASH_DIR=`dirname $0`




# You expect rows here for subjects that have NA for a particular column.
# Investigate when the numbers are very close to the total number of subjects.
echo "--------- $STUDY_SCHEMA  null values --------------"
grep $STUDY_SCHEMA "$FILE" | grep "had a null value" > $TMPFILE
$BASH_DIR/histogram.sh 9  $TMPFILE $TMPFILE_2


echo
# This message comes from values that don't appear for a particular person on a particular date.
# Marked as an error, it's mostly informational. If you see it for every subject, it could indicate 
# a problem worse than sparse data. ...and it takes many forms depending on the study.
# ERROR:events_mapping:no rows back from select addate, adcause from best.adju where id = %s and ( adcause=5 )
# ERROR:events_mapping:no rows back from select xpdat from best.xp where id = %s and ( xpsta=2 )

echo "--------- $STUDY_SCHEMA no rows back  that day--------------"
grep "no rows back" "$FILE" | grep $STUDY_SCHEMA | grep -v __init__ |  wc -l
grep "no rows back" "$FILE" | grep $STUDY_SCHEMA | grep -v __init__ | awk '{print "t:"$32"-c:"$34"-v:"$38"-c:"$40}' | sort -u




# OTHERS?
grep ERROR "$FILE" | grep -v "had a null value" | grep -v "no rows back" | grep -v __init__


