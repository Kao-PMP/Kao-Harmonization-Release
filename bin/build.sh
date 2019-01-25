#!/usr/bin/env bash

# build.sh <phase>  <environment>
#
# creates a db, runs the ddl, imports BEST csv files, imports OHDSI, imports descriptions and mapping tables
# maps from BEST to OHDSI (TODO)
# creates calculated fields (TODO)
# extracts categorized values for a ML project (TODO)
#
# phases: PIP3, OHDSI, TEST, UTEST,  BUILD, META, TRUNCATE, MIGRATE, CHECK, CALCULATE, EXTRACT, SHORT, FASTALL, ALL
#  PIP3   pip3 installs necessary packages for python
#  OHDSI imports an ohdsi starter database in to a new database, after dropping the existing one
#  TEST  runs sql tests
#  UTEST  runs python unit tests
#  BUILD imports a study's data from csv files
#  META  imports the mapping information
#  MIGRATE imports study data into the OHDSI tables, after truncating them
#  CALCULATE creates new ohdsi values from existing ohdsi values
#  EXTRACT extracts data from OHDSI, categorizes is and builds a csv file
#
#  CHECK  runs consistency checks
#  ANALYZE analyzes, makes readable the output from the consistency checks
#  REPORT a meta-level report of the mapping
#  
#  SHORT, FASTALL, ALL are different groupings of the commands above
#
# environment: DEV, TEST, PMP, DOCKER
#   locations of things are hard-coded differently for each environment
#
# assumes it's running in the base directory of the project
# assumes there's a vocabulary populated OHDSI in backups
#
# NB I know this Bash is getting crufty.

if [[ $# -ne 2 ]]
then
    echo "usage: build.sh <phase> <env>"
    echo "  phase is one of MIGRATE, CALCULATE, EXTRACT, or many others"
    echo "  env is one of TEST, PMP, DEV, or others"
    echo " I only got $# arguments. Please try again."
    exit 1
fi

PHASE=$1
ENV=$2


set -e 
set -o pipefail

MAX_STUDIES=5
#declare -a STUDY_NAMES=('PARADIGM' )
#declare -a STUDY_NAMES=('BEST' 'HFACTION' 'SCDHEFT' 'TOPCAT' )

declare -a STUDY_NAMES=('BEST' 'HFACTION' 'SCDHEFT' 'TOPCAT' 'PARADIGM' )
# used to find the study_id, depends on the order here being the same as the ids in the database TODO
declare -a STUDY_NAMES_ALL=('BEST' 'HFACTION' 'SCDHEFT' 'TOPCAT' 'PARADIGM' )

USER=`whoami`

# ADD THIS
#./attr_label.R studies/HF_ACTION_2015a/Data_DR/barrier.sas7bdat 2> /dev/null | grep "\[1]"   | sed -e "s/\[1\]//"



# ---- user modifiable stuff below here ----
EXTRACT_ID=1001


if [[ $ENV = 'PMP' ]]
then
    OHDSI_BASE=/mnt/workspace/researcher_data/ohdsi_201709.no_owner.gz
    PROJECT_DIR=/mnt/workspace/Harmonization/back_end
    STUDIES_DIR=/mnt/workspace/researcher_data/studies
    DBNAME=heart_db
    USER=harmon
fi

if [[ $ENV = 'TEST' ]]
then
    OHDSI_BASE=/Users/christopherroeder/backups/posterity/ohdsi_20170907.no_owner.gz
    PROJECT_DIR=/users/christopherroeder/work/git/test/back_end
    STUDIES_DIR=~/work/local/studies
    DBNAME="heart_test_$(date +%Y%m%d)"
fi

if [[ $ENV = 'DEV' ]]
then
    OHDSI_BASE=/home/croeder/work_local/ohdsi_20170907.no_owner
    OHDSI_BASE=/Users/christopherroeder/backups/posterity/ohdsi_20170907.no_owner.gz
    PROJECT_DIR=/users/christopherroeder/work/git/back_end
    STUDIES_DIR=~/work/local/studies
    DBNAME="heart_20180509"
fi

if [[ $ENV = 'MISC' ]]
then
    OHDSI_BASE="/Users/laurastevens/Dropbox/Graduate School/Harmonization/back_end/backups/posterity/ohdsi_20170907.no_owner.gz"
    OHDSI_BASE=/Users/croeder/work/dkao/test_install_2/back_end/backups/ohdsi_20170907.no_owner.gz
    PROJECT_DIR="/Users/laurastevens/Dropbox/Graduate\ School/Harmonization/back_end"
fi

# Docker
if [[ $ENV = 'DOCKER' ]]
then
    STUDIES_DIR=/home/croeder/work_local/studies
    #export PGHOST="10.0.2.2"
fi


# ---- user modifiable stuff above here ----

function find_study_id {
    # 1st arg is study_name
    # returns study_id (number)
    looking_for=$1
    study_id=1
    retval=0
    for name in ${STUDY_NAMES_ALL[@]}
    do
        if [[ $name == $looking_for ]]
        then
            retval=$study_id
        fi 
        study_id=$(( $study_id + 1 ))
    done
    echo "find_study_id $looking_for $retval"
    echo $retval
    return 0
}

function elementIn {
# arg1: what you're looking for
# arg2: the array
# returns: 0 when found
# Ex. elementIn "PARADIGM" "STUDY_NAMES[@]"
# check $? for 1 or 0


    local match="$1"
    declare -a test_list=("${!2}")
    local e 
    for e in ${test_list[@]}
    do 
        if [[ "$e" == "$match" ]] 
        then
            echo -n "found"; 
        fi
    done
  return 0 
}

if [[ "true" ]]
then
    echo "build.sh: argument is: $PHASE $MIGRATE $CALCULATE $EXTRACT"

    if [[ $PHASE == 'SHORT' ]]; then
        UTEST=0
        TEST=0
        BUILD=0
        META=0
        TRUNCATE=1
        MIGRATE=1
        CHECK=0
        CALCULATE=1
        EXTRACT=1
    fi
    if [[ $PHASE == 'FASTALL' ]]; then
        UTEST=0
        TEST=0
        OHDSI=1
        BUILD=1
        META=1
        MIGRATE=1
        CHECK=0
        CALCULATE=1
        EXTRACT=1
    fi
    if [[ $PHASE == 'ALL' ]]; then
        PIP3=1
        OHDSI=1
        UTEST=1
        TEST=1
        BUILD=1
        META=1
        MIGRATE=1
        CHECK=1
        REPORT=1
        CALCULATE=1
        EXTRACT=1
        ANALYZE=1
    fi

    if [[ $PHASE == 'OHDSI' ]]; then
        OHDSI=1
    fi
    if [[ $PHASE == 'UTEST' ]]; then
        UTEST=1
    fi
    if [[ $PHASE == 'TEST' ]]; then
        TEST=1
    fi
    if [[ $PHASE == 'TRUNCATE' ]]; then
        TRUNCATE=1
    fi
    if [[ $PHASE == 'BUILD' ]]; then
        BUILD=1
    fi
    if [[ $PHASE == 'META' ]]; then
        META=1
    fi
    if [[ $PHASE == 'MIGRATE' ]]; then
        MIGRATE=1
    fi
    if [[ $PHASE == 'CHECK' ]]; then
        CHECK=1
    fi
    if [[ $PHASE == 'REPORT' ]]; then
        REPORT=1
    fi
    if [ $PHASE == 'CALCULATE' ]; then
        CALCULATE=1
    fi
    if [ $PHASE == 'EXTRACT' ]; then
        EXTRACT=1
    fi
    if [ $PHASE == 'ANALYZE' ]; then
        ANALYZE=1
    fi
    if [ $PHASE == 'PIP3' ]; then
        PIP3=1
    fi
#done
fi
    echo "build.sh: argument is: $PHASE $MIGRATE $CALCULATE $EXTRACT"





function loadPARADIGM() {
    echo "build.sh: LOADING PARADIGM"
    file="${STUDIES_DIR}/PARADIGM/test.csv"
    table="test"
	./HeartData/load_csv.py $DBNAME "paradigm" $file $table $USER $PGHOST
    if [[ $? > 0 ]]; then
        echo "build.sh: error loading PARADIGM"
        exit 1;
    fi
}

function loadTOPCAT() {
    for file in \
            "${STUDIES_DIR}/TOPCAT/data/t002.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t004.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t005.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t003.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t010.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t011.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t006.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t008.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t031.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t030.csv" \
            "${STUDIES_DIR}/TOPCAT/data/t079.csv" \
            "${STUDIES_DIR}/TOPCAT/data/q002.csv"
    do
       echo "build.sh: LOADING TOPCAT file: \"$file\" $DBNAME $USER"
	    table=$(basename "$file" | sed s/.csv//)
	    ./HeartData/load_csv.py $DBNAME "topcat" $file $table $USER $PGHOST
        if [[ $? > 0 ]]; then
            echo "build.sh: error loading TOPCAT"
            exit 1;
        fi
    done
}


function loadSCDHeFT() {
    for file in \
        "${STUDIES_DIR}/SCD-HeFT/data/baseline_new.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/basecrf.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/ecg.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/rdemog.csv" \
        "${STUDIES_DIR}/SCD-HeFt/data/death.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/endpt_new.csv"
    do
       echo "build.sh: LOADING SCD-HeFT file: \"$file\" $DBNAME $USER"
	    table=`basename $file | sed s/.csv//`
	    ./HeartData/load_csv.py $DBNAME "scdheft" $file $table $USER $PGHOST
        if [[ $? > 0 ]]; then
            echo "build.sh: error loading SCD-HeFT"
            exit 1;
        fi
    done
}

function loadHFAction() {
    # HF-ACTION
    # see convert_sas.R
    for file in ${STUDIES_DIR}/HF_ACTION_2015a/Data_DR/*.csv
    do
	table=$(basename "$file" | sed s/.csv//)
        echo "build.sh: LOADING HF-action  db:$DBNAME file:$file table:$table user:$USER host:$PGHOST"
	./HeartData/load_csv.py $DBNAME "hfaction" $file $table $USER $PGHOST
        if [[ $? > 0 ]]; then
            echo "build.sh: error loading HF-Action"
            exit 1;
        fi
    done
}

function loadBEST() {
    # BEST
    for file in ${STUDIES_DIR}/BEST/best_csv/*.csv
    do
        echo "build.sh: LOADING BEST \"$file\" $DBNAME $USER "
	    table=$(basename "$file" | sed s/.csv//)
	    ./HeartData/load_csv.py $DBNAME "best" $file $table $USER $PGHOST
        if [[ $? > 0 ]]; then
            echo "build.sh: error loading best"
            exit 1;
        fi
    done
}


## --------- MAIN -----------
# NB these commands have to run (mostly) in the order they are present!

#PIP3
if [[ $PIP3 > 0 ]]; then
    pip3 install pandas
    pip3 install sqlalchemy
    pip3 install psycopg2
    pip3 install argh
fi

# OHDSI load the ohdsi starter database
if [[ $OHDSI > 0 ]]; then
    ##createdb $USER
    echo "build.sh: ***DROP***  $DBNAME"
    echo "drop database \"$DBNAME\"" | psql 
    echo "build.sh: OHDSI $DBNAME $PGUSER $USER"
    echo ""

    createdb $DBNAME

    ### OHDSI
    echo "===================OHDSI======================"
    echo "build.sh: OHDSI $DBNAME $OHDSI_BASE"
    gunzip -c "$OHDSI_BASE" |  psql  $DBNAME
    #cat "$OHDSI_BASE" |  psql --username=$PGUSER  $DBNAME
    if [[ $? > 0 ]]; then
        echo "build.sh: error loading ohdsi"
        exit 2;
    fi

    ## CONCEPTS
    echo "build.sh: ============= building indeces... ============"
    cat "${PROJECT_DIR}/sql/concept.sql" |  psql $DBNAME
    ###cat "${PROJECT_DIR}/ddl/indeces.sql" |  psql $DBNAME
    #echo "\d observation " |  psql $DBNAME 
    #echo "\d measurement " |  psql $DBNAME 
    #echo "\d concept " |  psql $DBNAME 
fi

if [[ $TEST > 0 ]]; then
    RES=$(cat sql/test_1.sql | psql -qtAX $DBNAME | tail -1)
    if [[ $RES == 'f' ]]; then
        echo "SQL test 1 failed"
    else
        echo "SQL test 1 passed"
    fi
fi

# This  runs python unit tests.
if [[ $UTEST > 0 ]]; then
    python -m unittest discover
    if [[ $? > 0 ]]; then
        echo "build.sh: error in unittests"
        exit 3;
    fi
fi

## BUILD load the study data
if [[ $BUILD > 0 ]]; then

    element_found=$(elementIn "PARADIGM" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading paradigm;"
        echo "create schema paradigm;" | psql $DBNAME
        loadPARADIGM
    else
        echo "NOT loading paradigm; -->\"$element_found\"<--  .."
    fi

    element_found=$(elementIn "TOPCAT" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading topcat;" 
        echo "create schema topcat;" | psql $DBNAME
        loadTOPCAT
    fi

    element_found=$(elementIn "SCDHEFT" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading scdft;" 
        echo "create schema scdheft;" | psql $DBNAME
        loadSCDHeFT
    fi

    element_found=$(elementIn "HFACTION" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading hfaction;" 
        echo "create schema hfaction;" | psql $DBNAME
        loadHFAction
    fi

    element_found=$(elementIn "BEST" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading best;"
        echo "create schema best;" | psql $DBNAME
        loadBEST
    fi
fi

if [[ $META > 0 ]]; then
    ### MAPPING and analysis metadate
    #echo "study concept and value.."
    #psql $DBNAME < ddl/study_concept_type.sql
    #psql $DBNAME < ddl/study_concept_value.sql
    # (optional) ./columns.py $DBNAME $USER

    echo "drop table study;" | psql $DBNAME
    echo "drop table extract_study;" | psql $DBNAME
    echo "drop table vocabulary_concepts;" | psql $DBNAME
    echo "drop table table_column;" | psql $DBNAME

    echo "drop table study_to_ohdsi_mapping;" | psql $DBNAME

    echo "drop table ohdsi_calculation_function;" | psql $DBNAME
    echo "drop table ohdsi_calculation_argument;" | psql $DBNAME

    echo "drop table categorization_function_metadata;" | psql $DBNAME
    echo "drop table categorization_function_parameters;" | psql $DBNAME
    echo "drop table categorization_function_qualifiers;" | psql $DBNAME
    echo "drop table categorization_function_table;" | psql $DBNAME

    echo "drop table events_mapping;" | psql $DBNAME


    echo "study"
    psql $DBNAME < backups/study.dump

    echo "extract_study"
    psql $DBNAME < backups/extract_study.dump

    echo "vocabulary_concept"
    psql $DBNAME < backups/vocabulary_concept.dump

    echo "table_column"
    psql $DBNAME < backups/table_column.dump

    echo "study_to_ohdsi_mapping"
    psql $DBNAME < backups/study_to_ohdsi_mapping.dump
    echo "ohdsi_calculation_function"
    psql $DBNAME < backups/ohdsi_calculation_function.dump
    echo "ohdsi_calculation_argument"
    psql $DBNAME < backups/ohdsi_calculation_argument.dump

    echo "categorization_function_meta"
    psql $DBNAME < backups/categorization_function_metadata.dump
    echo "categorization_function_parameters"
    psql $DBNAME < backups/categorization_function_parameters.dump
    echo "categorization_function_qualifiers"
    psql $DBNAME < backups/categorization_function_qualifiers.dump
    echo "categorization_function_table"
    psql $DBNAME < backups/categorization_function_table.dump

    echo "events_mapping"
    psql $DBNAME < backups/events_mapping.dump
fi


### MIGRATE
# NB migrate drops in a manner similar to the TRUNCATE command 
if [[ $MIGRATE > 0 ]]; then
    for STUDY in "${STUDY_NAMES[@]}"
    do
        echo "build.sh: MIGRATE $DBNAME $USER $STUDY"
        STUDY_LOWER=$(echo "$STUDY" | tr '[:upper:]' '[:lower:]')
        LOG_FILE=migrate_${STUDY_LOWER}.log
        ./HeartData/migrate.py $DBNAME $USER $STUDY &> $LOG_FILE
        if [[ $? > 0 ]]; then
            echo "build.sh: error migrating"
            exit 5;
        fi
    done
fi

## create CALCULATED fields
if [[ $CALCULATE > 0 ]]; then
    echo "MAX_STUDIES = $MAX_STUDIES"
    for STUDY in "${STUDY_NAMES[@]}"
    do
        echo "build.sh: CALCULATE $DBNAME $STUDY "
        STUDY_LOWER=$(echo "$STUDY" | tr '[:upper:]' '[:lower:]')
        LOG_FILE=calculate_${STUDY_LOWER}.log
        ./HeartData/calculate.py $DBNAME $USER $STUDY &> $LOG_FILE
        if [[ $? > 0 ]]; then
            echo "build.sh: error calculating $STUDY"
            exit 7;
        fi
    done
fi

## EXTRACT categorized values for ML
if [[ $EXTRACT > 0 ]]; then
    for STUDY in "${STUDY_NAMES[@]}"
    do
        STUDY_LOWER=$(echo "$STUDY" | tr '[:upper:]' '[:lower:]')
        LOG_FILE=extract_${STUDY_LOWER}.log
        echo "build.sh: EXTRACT db:$DBNAME user:$USER study_name:$STUDY $LOG_FILE"
        ./HeartData/extract.py $DBNAME $USER $STUDY $EXTRACT_ID &> $LOG_FILE
        if [[ $? > 0 ]]; then
           echo "build.sh: error extracting"
           exit 8;
        fi
    done
fi


if [[ $CHECK > 0 ]]; then
    for STUDY in "${STUDY_NAMES[@]}"
    do
        echo "build.sh: CHECK $DBNAME $STUDY "
        STUDY_LOWER=$(echo "$STUDY" | tr '[:upper:]' '[:lower:]')
        LOG_FILE=consistency_${STUDY_LOWER}.log
        ./HeartData/consistency.py $DBNAME $USER $STUDY &> $LOG_FILE
        if [[ $? > 0 ]]; then
            echo "build.sh: error consistency check"
            exit 6;
        fi
    done


    for STUDY in "${STUDY_NAMES[@]}"
    do
        STUDY_LOWER=$(echo "$STUDY" | tr '[:upper:]' '[:lower:]')
        LOG_FILE=consistency_stats_${STUDY_LOWER}.log
        ./HeartData/consistency_stats.py $DBNAME $USER $STUDY &> $LOG_FILE
        if [[ $? > 0 ]]; then
            echo "build.sh: error consistency_stats check"
            exit 6;
        fi
    done
fi

#ANALYZE
if [[ $ANALYZE > 0 ]]; then
    for STUDY in "${STUDY_NAMES[@]}"
    do
        for TYPE in calculate consistency extract migrate 
        do
            STUDY_LOWER=$(echo "$STUDY" | tr '[:upper:]' '[:lower:]')
            echo "study:\"$STUDY_LOWER\" type:\"$TYPE\" before"   
            find_study_id $STUDY
            STUDY_ID=$?
            echo "study:\"$STUDY_LOWER\" type:\"$TYPE\"  study_id:${STUDY_ID} "

            echo "===================================" >> ${STUDY_LOWER}_${TYPE}_summary
            echo "study:\"$STUDY_LOWER\" type:\"$TYPE\"" >> ${STUDY_LOWER}_${TYPE}_summary
            echo "===================================" >> ${STUDY_LOWER}_${TYPE}_summary
            bin/analyze_${TYPE}_output.sh ${TYPE}_${STUDY_LOWER}.log ${STUDY_LOWER} ${STUDY_ID} >> ${STUDY_LOWER}_${TYPE}_summary

            cat ${STUDY_LOWER}_${TYPE}_summary >> ${STUDY_LOWER}_summary
        done
        #cat consistency_stats_$STUDY_LOWER.out >> ${STUDY_LOWER}_summary
    done
fi


if [[ $REPORT > 0 ]]; then
    for STUDY in "${STUDY_NAMES[@]}"
    do
        echo "build.sh: CHECK $DBNAME $STUDY $STUDY" 
        STUDY_LOWER=$(echo "$STUDY" | tr '[:upper:]' '[:lower:]')
        LOG_FILE=report_${STUDY_LOWER}.log
        ./HeartData/report.py $DBNAME $USER $STUDY &> $LOG_FILE
        if [[ $? > 0 ]]; then
            echo "build.sh: error report check"
            exit 6;
        fi
    done


    for STUDY in "${STUDY_NAMES[@]}"
    do
        STUDY_LOWER=$(echo "$STUDY" | tr '[:upper:]' '[:lower:]')
        LOG_FILE=report_extraction_${STUDY_LOWER}.log
        ./HeartData/report_extraction.py $DBNAME $USER $STUDY $EXTRACT_ID  &> $LOG_FILE
        if [[ $? > 0 ]]; then
            echo "build.sh: error report_extraction check"
            exit 6;
        fi
    done
fi


