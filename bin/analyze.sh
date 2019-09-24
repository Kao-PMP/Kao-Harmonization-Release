#ANALYZE
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
return 0
