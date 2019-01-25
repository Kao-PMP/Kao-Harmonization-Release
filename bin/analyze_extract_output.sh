#!/usr/bin/env bash

# analyze_extract_out <file>
#
# croeder 10/2017


FILE="$1"
TMPFILE=/tmp/analyze_extract_output.tmp
TMPFILE_2=/tmp/analyze_extract_output_2.tmp
BASH_DIR=`dirname $0`


echo "=== missing value ==="
grep "missing value"  "$FILE"  > $TMPFILE
cat $TMPFILE  | awk -F: '{print $5}' | awk -F, '{print $1}' | sort -u > $TMPFILE_2
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
for word in `cat $TMPFILE_2`
do
    echo -n "$word:"
    grep $word $TMPFILE | wc -l    
done
IFS=$SAVEIFS

echo "=== no entity for ==="
grep "no entity for" "$FILE" > $TMPFILE
$BASH_DIR/histogram.sh 7  $TMPFILE $TMPFILE_2

echo "=== verify bogus ==="
grep "verify bogus" "$FILE"  > $TMPFILE
cat $TMPFILE  | awk -F: '{print $5}' | awk -F, '{print $1}' | sort -u > $TMPFILE_2
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
for word in `cat $TMPFILE_2`
do
    echo -n "$word:"
    grep $word $TMPFILE | wc -l    
done
IFS=$SAVEIFS
return 0;
