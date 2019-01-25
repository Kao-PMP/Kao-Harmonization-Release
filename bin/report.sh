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


