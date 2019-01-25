#!/usr/bin/env bash


# Run paradigm, sort the csv and compare to what came from Dave's pipeline.
#    compare those results with what I've gotten previously because they are not perfect.
   
    ls ../paradigm.csv > ../paradigm_sorted.csv 
    /usr/bin/sort ../paradigm.csv > ../paradigm_sorted.csv  2> /dev/null
    ../bin/compare_csv.sh ../paradigm_sorted.csv ../backups/paradigm_phenotype_table_dr_id_sorted.csv > /tmp/paradigm_comparison.txt 2> /dev/null
    diff ../resource/paradigm_csv_comparison.txt /tmp/paradigm_comparison.txt > /dev/null 2> /dev/null
    if [ $? -ne 0 ]
    then 
        echo "error in paradigm csv test"
        #cat /tmp/paradigm_comparison.txt
    else
        echo "paradigm csv test OK"
        #cat /tmp/paradigm_comparison.txt
    fi
