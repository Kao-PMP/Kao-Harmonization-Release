#!/usr/bin/env bash

# show categorization mappings

if ((  $# < 1 )) ; then
    echo ""
    echo "usage: show_categorization_mappings.sh study_id"
    echo ""
    exit
fi

EXTRACT_STUDY_ID=$1

echo "Categorization Mappings"
echo "
	SELECT m.long_name, m.short_name as abbr, m.from_vocabulary_id as vocab, m.from_concept_code as code, 
        substring(cm.concept_name, 1,10 ) as concept,
		m.function_name, 
		p.value_limit as limit, p.from_string,      
        substring(cp.concept_name, 1,10) as concept,
        p.rank
		
	FROM  categorization_function_metadata m
	left JOIN  categorization_function_parameters p
		ON m.extract_study_id = p. extract_study_id
	   AND m.function_name = p.function_name
	   AND m.long_name = p.long_name
	   AND m.rule_id = p.rule_id
	JOIN concept cm
		ON m.from_vocabulary_id = cm.vocabulary_id
	   AND m.from_concept_code = cm.concept_code
	left JOIN concept cp
	   ON p.from_concept_id = cp.concept_id
	WHERE m.extract_study_id = $EXTRACT_STUDY_ID
	ORDER BY m.short_name, cm.concept_code
" | psql

