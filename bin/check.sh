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
