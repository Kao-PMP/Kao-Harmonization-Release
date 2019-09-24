#!/usr/bin/env bash

echo "<pre>"
echo "<h2> Categorization Mappings </h2>"
	#WHERE m.extract_study_id = 20001
echo "
	SELECT  m.short_name as abbreviation, cm.concept_name
	FROM  categorization_function_metadata m
	JOIN concept cm
		ON m.from_vocabulary_id = cm.vocabulary_id
	   AND m.from_concept_code = cm.concept_code
	WHERE m.extract_study_id = 5001
	ORDER BY m.short_name
" | psql

echo "</pre>"
