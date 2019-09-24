#!/usr/bin/env bash

# show use of a given concept_code
if ((  $# < 3 )) ; then
    echo ""
    echo "usage: show_concept_usage.sh study_id, vocabulary_id, concept_code"
    echo ""
    exit
fi

STUDY_ID=$1
VOCABULARY_ID=$2
CONCEPT_CODE=$3

echo "QUERYING FOR: study: study_id:$STUDY_ID concept:$CONCEPT_CODE vocabulary:$VOCABULARY_ID"

echo ""
echo "CONCEPT ----------------------------------"
echo "select  concept_id, vocabulary_id, concept_code, concept_name from concept where concept_code = '$CONCEPT_CODE' and vocabulary_id = '$VOCABULARY_ID' " | psql

echo ""
echo "STUDY MAPPING (import) -------------------"
echo "select * from study_to_ohdsi_mapping m where concept_code = '$CONCEPT_CODE' and vocabulary_id = '$VOCABULARY_ID' and study_id = $STUDY_ID" | psql

echo "STUDY MAPPING arguments to:"
echo "select * from study_mapping_arguments where to_concept_code = '$CONCEPT_CODE' and to_concept_vocabulary_id = '$VOCABULARY_ID' and study_id = $STUDY_ID" | psql

echo "STUDY MAPPING arguments from:"
echo "select * from study_mapping_arguments where mapped_concept_code = '$CONCEPT_CODE' and mapped_concept_vocabulary_id = '$VOCABULARY_ID' and study_id = $STUDY_ID" | psql



echo ""
echo "CALCULATION ------------------------------"
echo "select * from ohdsi_calculation_function where to_concept_code = '$CONCEPT_CODE' and to_vocabulary_id = '$VOCABULARY_ID' and study_id = $STUDY_ID" | psql

echo "Input Concept:"
echo "select c.concept_name, a.*  from ohdsi_calculation_argument a, concept c where a.to_concept_code = '$CONCEPT_CODE' and a.to_vocabulary_id = '$VOCABULARY_ID' and study_id = $STUDY_ID and a.concept_code = c.concept_code and a.vocabulary_id = c.vocabulary_id" | psql

echo "Destination Concept:"
echo "select a.*, c.concept_name from ohdsi_calculation_argument a, concept c where a.concept_code = '$CONCEPT_CODE' and a.vocabulary_id = '$VOCABULARY_ID' and study_id = $STUDY_ID and a.to_vocabulary_id = c.vocabulary_id and a.to_concept_code = c.concept_code" | psql

echo ""
echo "CATEGORIZATION (export) ------------------"
echo "select * from categorization_function_metadata where from_concept_code = '$CONCEPT_CODE' and from_vocabulary_id = '$VOCABULARY_ID' " | psql
echo "parameters:"
echo "select * from categorization_function_parameters p, concept c where p.from_concept_id = c.concept_id and c.concept_code =  '$CONCEPT_CODE' and c.vocabulary_id = '$VOCABULARY_ID' " | psql

echo ""
