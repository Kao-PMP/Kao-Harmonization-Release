#!/usr/bin/env bash

# OHDSI load the ohdsi starter database

#DBNAME=$1
DBNAME=$PGDATABASE
PROJECT_DIR=/opt/local/harmonization/deployment
OHDSI_BASE=$PROJECT_DIR/ohdsi_20170907.no_owner.gz

set -e 
set -o pipefail 

    ### OHDSI
    echo "ohdsi.sh: OHDSI $DBNAME $OHDSI_BASE"
    gunzip -c "$OHDSI_BASE" |  psql  $DBNAME
    if [[ $? -ne 0  ]]; then
        echo "ohdsi.sh: error loading ohdsi $OHDSI_BASE val:$?"
        exit 2;
    fi

    ## CONCEPTS
    pwd
    echo "ohdsi.sh CONCEPTS step, project dir:$PROJECT_DIR, db:$DBNAME"
    cat "../sql/concept.sql" |  psql $DBNAME
    if [[ $?  -ne 0 ]]; then
        echo "ohdsi.sh: error loading ohdsi $(pwd)"
        exit 3;
    fi

    ###cat "${PROJECT_DIR}/ddl/indeces.sql" |  psql $DBNAME # TODO
