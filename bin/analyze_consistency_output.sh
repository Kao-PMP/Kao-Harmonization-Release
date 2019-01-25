#!/usr/bin/env bash
#
# analyze_consistency_output <file>
#
# Sort throught the output from consistency.py.
#
# croeder 10/2017

FILE="$1"
echo "searching $FILE, ideally these numbers are very low. At least they should not be for all patients."

TARGET_1="ohdsi lookup failed"
echo "ERROR TARGET: $TARGET_1:"
for WORD in `grep "$TARGET_1" "$FILE" | awk '{print $11}' | sort -u `
do
    echo -n $WORD
    grep "$TARGET_1" "$FILE" | grep $WORD |  wc -l
done
echo
echo 
echo
TARGET_2="check_values_are_consistent_with_compare_count"
echo "ERROR TARGET: $TARGET_2:"
for WORD in `grep "$TARGET_2" "$FILE" | awk '{print $6}' | sort -u `
do
    echo -n $WORD
    grep "$TARGET_2" "$FILE" | grep $WORD |  wc -l
done
echo
echo
echo
TARGET_3="get_patient_visits"
echo "ERROR TARGET: $TARGET_3:"
for WORD in `grep "$TARGET_3" "$FILE" | awk '{print $6}' | sort -u `
do
    echo -n $WORD
    grep "$TARGET_3" "$FILE" | grep $WORD |  wc -l
done

echo
echo
echo
TARGET_3_5="OHDSI is missing values"
echo "ERROR TARGET: $TARGET_3_5:"
for WORD in `grep "$TARGET_3_5" "$FILE" | awk '{print $12}' | sort -u `
do
    echo -n $WORD
    grep "$TARGET_3_5" "$FILE" | grep $WORD |  wc -l
done

echo 
echo
echo "OTHER ERRORS ?:"
grep ERROR "$FILE" | grep -v "$TARGET_1" | grep -v "$TARGET_2" | grep -v "$TARGET_3 " | grep -v "$TARGET_3_5"



echo
echo "WARNINGS..."
echo 
echo
TARGET_4="no data on any day for table"
echo "WARNING TARGET: $TARGET_4:"
for WORD in `grep WARNING "$FILE" | grep  "$TARGET_4" | awk '{print $7}' | sort -u `
do
    echo -n $WORD
    grep "$TARGET_4" "$FILE" | grep $WORD |  awk '{print $7}'| sort -u
done
echo
echo 
echo
TARGET_5="might want to look at"
echo "WARNING TARGET: $TARGET_5:"
grep WARNING "$FILE" | grep  "$TARGET_5"

echo 
echo
echo "OTHER WARNINGS ?:"
grep WARNING "$FILE" | grep -v "$TARGET_4" | grep -v "$TARGET_5"

echo 
echo "INFO..."
echo
echo
TARGET_6="got no rows"
echo "INFO TARGET: $TARGET_6:"
for WORD in `grep INFO "$FILE" | grep  "$TARGET_6" | awk '{print $10}' | sort -u `
do
    echo -n $WORD
    grep INFO "$FILE" | grep $WORD | wc -l
done

return 0
