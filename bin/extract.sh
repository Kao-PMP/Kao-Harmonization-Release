## EXTRACT categorized values for ML
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
return 0;
