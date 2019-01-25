#!/usr/bin/env bash

# Builds a frequency distribution of variables that had issues in the calculation phase.
# Depends on log files from the calculation phase. Uses a script, histogram.sh 
# and related temporary files in /tmp.

FILE="$1"
SCHEMA=$2
STUDY_ID=$3
TMPFILE=/tmp/analyze_calculate_out.tmp
TMPFILE_2=/tmp/analyze_calculate_out_2.tmp
BASH_DIR=`dirname $0`

echo "(analyze_calculate)== wrong number of values (for any study) =================="
echo "(analyze calculate)-- study file:$FILE schema:$SCHEMA study:$STUDY_ID -----------"
grep ERROR "$FILE" | grep "wrong number of values" | grep "study_id:$STUDY_ID" > $TMPFILE
wc -l $TMPFILE
$BASH_DIR/histogram.sh  13 $TMPFILE  $TMPFILE_2
wc -l $TMPFILE_2

echo "wrong number of values"
grep ERROR "$FILE" | grep -v "wrong number of values"


echo
echo "(analyze calculate) == No rows returned ==============="
echo "(analyze_calculate)-- study $STUDY_ID -----------"
grep WARNING "$FILE"   | grep  "No rows retur"  | grep "study:$STUDY_ID" > $TMPFILE
grep WARNING "$FILE"   | grep  "No rows retur"  | grep "study:$STUDY_ID" | awk -Fpair '{print $2}' | awk '{print $2}'|sort -u > $TMPFILE_2
for word in `cat $TMPFILE_2`
do
    echo -n "word: $word"
    grep $word $TMPFILE | wc -l
done



# OTHER WARNINGS?
echo "others 2"
grep WARNING "$FILE" | grep -v "No rows returned" | grep -v "no rows...SELECT"

echo 'done'

return 0
