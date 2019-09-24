#!/usr/bin/env bash

# show calculation mappings

if ((  $# < 1 )) ; then
    echo ""
    echo "usage: show_concept_usage.sh study_id"
    echo ""
    exit
fi

STUDY_ID=$1

echo "
	SELECT s.study_name, 
		c_fun.vocabulary_id, c_fun.concept_code, c_fun.concept_name, 
		f.function_name, 
		c_arg.vocabulary_id, c_arg.concept_code, c_arg.concept_name
	FROM
		ohdsi_calculation_function f 
		JOIN ohdsi_calculation_argument a 
			ON f.study_id = a.study_id
		   AND  f.to_vocabulary_id = a.to_vocabulary_id
		   AND  f.to_concept_code = a.to_concept_code
		   AND  f.function_name = a.function_name
		JOIN concept c_fun
			ON f.to_vocabulary_id = c_fun.vocabulary_id
		   AND  f.to_concept_code = c_fun.concept_code
		JOIN concept c_arg
			ON a.vocabulary_id = c_arg.vocabulary_id
		   AND  a.concept_code = c_arg.concept_code
		JOIN study s
			ON f.study_id = s.study_id
	WHERE
		s.study_id = $STUDY_ID
	ORDER BY study_name, c_fun.concept_code
" | psql
