#!/usr/bin/env bash
# load studies already known by the system
# TODO: drive this by meta data

DBNAME=$1
STUDIES_DIR=/opt/local/harmonization/deployment/studies
HOST="localhost:8000/"
# The order in this array relates to the study_id in the study table. TODO
declare -a STUDY_NAMES_ALL=('BEST' 'HFACTION' 'SCDHEFT' 'TOPCAT' 'PARADIGM' 'TEST')

# This array lists the studies we want to load.
#declare -a STUDY_NAMES=('BEST' 'HFACTION' 'SCDHEFT' 'TOPCAT' 'PARADIGM' )
declare -a STUDY_NAMES=('BEST' 'HFACTION' 'SCDHEFT' 'TOPCAT' 'PARADIGM' 'TEST')

set -e 
set -o pipefail 


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

function loadPARADIGM() {
    echo "load_studies.sh: LOADING PARADIGM"
    file="${STUDIES_DIR}/PARADIGM/test.csv"
    table="test"
    schema_table="paradigm.$table"
    echo "drop table $schema_table ;" | psql $DBNAME
    echo "drop table $table ;" | psql $DBNAME
	ehco " $DBNAME paradigm file:$file table:$table u:$PGUSER p:$PGPASSWORD h:$PGHOST"
	./HeartData/load_csv.py $DBNAME "paradigm" $file $table $PGUSER "$PGPASSWORD" $PGHOST
    if [[ $? > 0 ]]; then
        echo "load_studies.sh: error loading PARADIGM"
        exit 1;
    fi
    curl ${HOST}/ui/set_study_loaded/PARADIGM/
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
       echo "load_studies.sh: LOADING TOPCAT file: \"$file\" $DBNAME $PGUSER"
       pwd
	    table=$(basename "$file" | sed s/.csv//)
        schema_table="topcat.$table"
        echo "drop table $schema_table ;" | psql $DBNAME
    	echo "$DBNAME topcat f:$file t:$table u:$PGUSER p:$PGPASSWORD h:$PGHOST"
    	./HeartData/load_csv.py $DBNAME "topcat" $file $table $PGUSER "$PGPASSWORD" $PGHOST
        if [[ $? > 0 ]]; then
            echo "load_studies.sh: error loading TOPCAT"
            exit 1;
        fi
    done
    curl ${HOST}/ui/set_study_loaded/TOPCAT/
}


function loadSCDHeFT() {
    for file in \
        "${STUDIES_DIR}/SCD-HeFT/data/baseline_new.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/basecrf.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/ecg.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/rdemog.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/death.csv" \
        "${STUDIES_DIR}/SCD-HeFT/data/endpt_new.csv"
    do
       echo "load_studies.sh: LOADING SCD-HeFT file: \"$file\" $DBNAME $PGUSER"
	    table=`basename $file | sed s/.csv//`
        schema_table="scdheft.$table"
        echo "drop table $schema_table ;" | psql $DBNAME
	    echo " $DBNAME scdheft f:$file t:$table u:$PGUSER p:$PGPASSWORD h:$PGHOST"
	    ./HeartData/load_csv.py $DBNAME "scdheft" $file $table $PGUSER "$PGPASSWORD" $PGHOST
        if [[ $? > 0 ]]; then
            echo "load_studies.sh: error loading SCD-HeFT"
            exit 1;
        fi
    done
    curl ${HOST}/ui/set_study_loaded/SCDHEFT/
}

function loadHFAction() {
    # HF-ACTION
    # see convert_sas.R
    for file in ${STUDIES_DIR}/HF_ACTION_2015a/Data_DR/*.csv
    do
	table=$(basename "$file" | sed s/.csv//)
    schema_table="hfaction.$table"
    echo "drop table $schema_table ;" | psql $DBNAME
    echo "load_studies.sh: LOADING HF-action  db:$DBNAME file:$file table:$table user:$PGUSER host:$PGHOST"
	echo "$DBNAME hfaction f:$file t:$table u:$PGUSER p:$PGPASSWORD h:$PGHOST"
	./HeartData/load_csv.py $DBNAME "hfaction" $file $table $PGUSER "$PGPASSWORD" $PGHOST
        if [[ $? > 0 ]]; then
            echo "load_studies.sh: error loading HF-Action"
            exit 1;
        fi
    done
    curl ${HOST}/ui/set_study_loaded/HFACTION/
}

function loadBEST() {
    # BEST
    for file in ${STUDIES_DIR}/BEST/best_csv/*.csv
    do
        echo "load_studies.sh: LOADING BEST \"$file\" $DBNAME $PGUSER "
	    table=$(basename "$file" | sed s/.csv//)
        schema_table="best.$table"
        echo "drop table $schema_table ;" | psql $DBNAME
	    echo "$DBNAME best f:$file t:$table u:$PGUSER p:$PGPASSWORD h:$PGHOST"
	    ./HeartData/load_csv.py $DBNAME "best" $file $table $PGUSER "$PGPASSWORD" $PGHOST
        if [[ $? > 0 ]]; then
            echo "load_studies.sh: error loading best"
            exit 1;
        fi
    done
    curl ${HOST}/ui/set_study_loaded/BEST/
}


## BUILD load the study data
echo "load_studies()  $DBNAME"

    element_found=$(elementIn "PARADIGM" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading paradigm;"
        echo "create schema paradigm;" | psql $DBNAME
        loadPARADIGM
    else
        echo "NOT loading PARADIGM; -->\"$element_found\"<--  .."
    fi

    element_found=$(elementIn "TOPCAT" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading topcat;" 
        echo "create schema topcat;" | psql $DBNAME
        loadTOPCAT
    else
        echo "NOT loading TOPCAT; -->\"$element_found\"<--  .."
    fi

    element_found=$(elementIn "SCDHEFT" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading scdft;" 
        echo "create schema scdheft;" | psql $DBNAME
        loadSCDHeFT
    else
        echo "NOT loading SCDHEFT; -->\"$element_found\"<--  .."
    fi

    element_found=$(elementIn "HFACTION" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading hfaction;" 
        echo "create schema hfaction;" | psql $DBNAME
        loadHFAction
    else
        echo "NOT loading HFACTION; -->\"$element_found\"<--  .."
    fi

    element_found=$(elementIn "BEST" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading best;"
        echo "create schema best;" | psql $DBNAME
        loadBEST
    else
        echo "NOT loading BEST; -->\"$element_found\"<--  .."
    fi

    element_found=$(elementIn "TEST" "STUDY_NAMES[@]")
    if [[ $element_found == "found" ]]
    then
        echo "loading test;"
        echo "create schema test;" | psql $DBNAME
        loadTEST
    else
        echo "NOT loading TEST; -->\"$element_found\"<--  .."
    fi
