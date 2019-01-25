#!/usr/bin/env bash

DBNAME=$1
USER=christopherroeder

SCRIPT_DIR=$(dirname "$0")

for file in ../ohdsi_vocab_v5/*.csv
do
    echo "LOADING OHDSI $file"
    table=`basename $file | sed s/.csv//`
    $SCRIPT_DIR/../HeartData/load_csv.py $DBNAME $file $table $USER
    if [[ $? > 0 ]]; then
        echo "error loading best"
        exit 1;
    fi
done

