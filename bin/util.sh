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
