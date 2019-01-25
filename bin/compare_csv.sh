#!/usr/bin/env bash

#

# assumes a row with "person_id" is a header that is available in the first file
# assumes comma separated values

A=$1
B=$2
HEADER_ROW=`grep person_id $A | head -1 `
# N:number of columns
N=`cat $A | awk -F, '{print NF}' | sort -nu`
# skip the 1st column, the ids. I know paradigm has 40 columns (fix).
N=$(( N -1 ))
i=2
while [ $i -le $N ] 
do
    FIELD_NAME=`echo $HEADER_ROW | awk -F, -v COL=$i  '{print $COL}'`
    VALUES_A=$(cat $A | grep -v person_id | awk -F, -v COL=$i '{print $COL}' | grep -v NA | grep -v NULL | sort -u )
    VALUES_B=$(cat $B | grep -v person_id | awk -F, -v COL=$i '{print $COL}' | grep -v NA | grep -v NULL | sort -u )
    VALUES_A_LINE=$( echo $VALUES_A | tr -d '\n')
    VALUES_B_LINE=$( echo $VALUES_B | tr -d '\n')
    if [ "$VALUES_A_LINE" != "$VALUES_B_LINE" ]; then
        echo "$i:$FIELD_NAME different values: \"$VALUES_A_LINE\" :  \"$VALUES_B_LINE\""
    fi
    SUM_A=0
    SUM_B=0
    VA=0
    VB=0
    for v in $VALUES_A
    do
        VA=$(cat $A | grep -v person_id | awk -F, -v COL=$i '{print $COL}' | grep $v | wc -l)
        SUM_A=$(($SUM_A + $VA))

        VB=$(cat $B | grep -v person_id | awk -F, -v COL=$i '{print $COL}' | grep $v | wc -l)
        SUM_B=$(($SUM_B + $VB))

        if (( $VA != $VB && $v != 'NULL' && $v != 'NA' ))
        then 
            echo  "$i:$FIELD_NAME $v  count_A:$VA  count_B:$VB  "
        fi
    done
    if (( $SUM_A != $SUM_B ))
    then
        echo "$i:$FIELD_NAME  nulls: $SUM_A  $SUM_B"
    fi
    i=$(($i+1))
done
