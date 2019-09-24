select count(o.*), s.from_column as best, c.concept_id as con, c.vocabulary_id as vocab, c.concept_code as term, substring(c.concept_name, 1, 25) 
from study_to_ohdsi_mapping s, observation o, concept c 
where  o.observation_concept_id = c.concept_id 
and s.vocabulary_name = c.vocabulary_id 
and s.vocabulary_term_id = c.concept_code 
group by c.concept_id, c.concept_name, c.vocabulary_id, c.concept_code, s.from_column;
