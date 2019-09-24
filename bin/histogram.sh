#!/usr/bin/env bash

# histogram.sh <column number> <logfile> <tmp for wordfile> [<awk delimeter>]
#
# awk's out a column to get a list of unique words,
# then creats a frequency distribution for words in that column.
# Meaning, it tells you how often each of the values a column has appears in that column.
#
# croeder October 2017

ARGC=$#

column=$1
logfile=$2
wordfile=$3

if [[ $ARGC > 3 ]]
then
    delimiter=$4
    echo "histogram.sh:  column:$column, logfile:$logfile, wordfile:$wordfile delimeter:'$delimeter'"
    cat $logfile | awk -F$delimiter -v c=$column '{print $c}' | sort -u > $wordfile
else
    echo "histogram.sh:  column:$column, logfile:$logfile, wordfile:$wordfile"
    cat $logfile | awk -v c=$column '{print $c}' | sort -u > $wordfile
fi

for word in `cat $wordfile`
do
    echo -n "$word:"
    grep $word $logfile | wc -l    
done
