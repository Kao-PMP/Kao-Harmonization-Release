## create CALCULATED fields
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
