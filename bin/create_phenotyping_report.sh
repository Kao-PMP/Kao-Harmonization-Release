#!/bin/bash
#
# create_phenotyping_report.sh <study_id>
#
# A script to pass arguments for the different studies to a single phenotyping Rmd script using parameters.
# ...the convenience of a single copy of the script comes at the expense of enforcing some structure.
# We don't have to run this script from a particular directory. We find the files by having a set directory
# structure and orienting ourselves from the location of this script within it: DIR
# study_id is in the database table study and repeated/duplicated in the list of studies below. It's 0-based.
#
# directory structure
# <project-root>
#   bin/create_phenotyping_reports.sh (this file)
#   r_lang/phenotyping_script.Rmd
#   <study>.csv
#
# croeder Nov. 2017
 
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MD_FILE=phenotyping_script.Rmd
declare -a CSV_FILES=('best.csv' 'hfaction.csv' 'paradigm.csv' 'scdheft.csv' 'topcat.csv')
declare -a NUM_CLASSES=(5 6 6 4 5)

i=$1
echo $MD_FILE ${CSV_FILE[$i]} ${NUM_CLASSES[$i]}
Rscript -e "rmarkdown::render($MD_FILE, params = list( csv_file=\"${CSV_FILE[$i]}\", num_classes=${NUM_CLASSES[$i]}))"
