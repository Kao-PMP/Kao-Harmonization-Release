#!/usr/bin/env bash


 # P M P
#SCRIPTS=/mnt/workspace/output/scripts/
#OUTPUT=/mnt/workspace/output/new_reports
#echo "calc"
#$SCRIPTS/calculation_mappings.sh > $OUTPUT/calculation_mappings.html
#echo "cate"
#$SCRIPTS/categorization_mappings.sh > $OUTPUT/categorization_mappings.html
#echo "cate short"
#$SCRIPTS/categorization_mappings_short.sh > $OUTPUT/categorization_mappings_short.html
#echo "import"
#$SCRIPTS/import_mappings.sh > $OUTPUT/import_mappings.html

# HOME
SCRIPTS=./
OUTPUT=./
echo "calc"
$SCRIPTS/calculation_mappings.sh > $OUTPUT/calculation_mappings.html
echo "cate"
$SCRIPTS/categorization_mappings.sh > $OUTPUT/categorization_mappings.html
#echo "cate short"
#$SCRIPTS/categorization_mappings_short.sh > $OUTPUT/categorization_mappings_short.html
echo "import"
$SCRIPTS/import_mappings.sh > $OUTPUT/import_mappings.html


