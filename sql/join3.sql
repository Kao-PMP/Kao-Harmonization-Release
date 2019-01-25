-- should be same number of rows from each of these???

-- individual mappings:
-- this select may have more rows than attributes desired since an attribute may have more than one rule to map it, each applicable in different situations
-- pcrace for example goes into the observation table and the person table
select * from study_to_ohdsi_mapping where function_name is not null order by from_column;

select * from categorization_function_metadata m
where m.from_vocabulary_concept_id = 'x';

select * from categorization_function_metadata m
where m.from_vocabulary_concept_id != 'x';

-- select just to join the mappings
select s.from_column as best, s.vocabulary_term_id as ohdsi,  s.to_column, s.to_table, m.to_column 
from categorization_function_metadata m, study_to_ohdsi_mapping s
where s.vocabulary_name = m.from_vocabulary_id
and s.vocabulary_term_id = m.from_vocabulary_concept_id
order by s.from_column;


-- select the join on the mappings and add in the concept_id from OHDSI's concept table to legitimize the vocabulary ids and concept ids
select s.from_column as best, s.vocabulary_term_id as ohdsi,  m.to_column , c.concept_id
from categorization_function_metadata m, study_to_ohdsi_mapping s, concept c
where s.vocabulary_name = m.from_vocabulary_id
and s.vocabulary_term_id = m.from_vocabulary_concept_id
and s.vocabulary_name = c.vocabulary_id
and s.vocabulary_term_id = c.concept_code
and s.to_table = 'observation'
order by s.from_column;

-- add in actual observations. If this returns fewer rows, the migrate code may not be bringing over data that it should
select s.from_column as best,  c.concept_id, c.vocabulary_id as vocab, c.concept_code as term, m.to_column 
from categorization_function_metadata m, study_to_ohdsi_mapping s, observation o, concept c 
where  o.observation_concept_id = c.concept_id 
and s.vocabulary_name = c.vocabulary_id 
and s.vocabulary_term_id = c.concept_code 
and m.from_vocabulary_id = c.vocabulary_id 
and m.from_vocabulary_concept_id = c.concept_code 
and s.to_table = 'observation'
group by c.concept_id, c.concept_name, c.vocabulary_id, c.concept_code, s.from_column, m.to_column
order by s.from_column;

-- ideally this would be in a python script, rather than hard-coded sql and we could create a queries to see if the BEST input data had what appears to be missing in the abover query by mapping from the from_table field to an actual table name in a query.

--This might come in handy if you have concept_ids that seem to be missing
-- select count(*), value_as_string, observation_concept_id, observation_date 
-- from observation 
-- where observation_concept_id in (316998, 316866) 
-- group by value_as_string, observation_concept_id, observation_date;
