DBNAME=$1
USER=christopherroeder
### MIGRATE
# NB migrate drops in a manner similar to the TRUNCATE command 
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

