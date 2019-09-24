--
--    Copyright 2017 The Regents of the University of Colorado
--
--    Licensed under the Apache License, Version 2.0 (the "License")
--    you may not use this file except in compliance with the License.
--    You may obtain a copy of the License at
--
--        http://www.apache.org/licenses/LICENSE-2.0
--
--    Unless required by applicable law or agreed to in writing, software
--    distributed under the License is distributed on an "AS IS" BASIS,
--    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
--    See the License for the specific language governing permissions and
--    limitations under the License.
--


drop table if exists  categorization_function_metadata;
CREATE TABLE categorization_function_metadata (
    extract_study_id integer NOT NULL,
    function_name character varying(100) NOT NULL,
    long_name character varying(100) NOT NULL,
    rule_id character varying(20) NOT NULL,
    from_vocabulary_id character varying(100) NOT NULL,
    from_concept_code character varying(100) NOT NULL, -- from_vocabulary_concept_id character varying(100) NOT NULL,
    comment character varying(256),
    from_table character varying(20),
    short_name character(6),
    Constraint PK_categorization_function_metadata  PRIMARY KEY (extract_study_id, function_name, long_name, rule_id)
);

drop table if exists categorization_function_parameters;
CREATE TABLE categorization_function_parameters (
    extract_study_id integer NOT NULL,
    function_name character varying(100) NOT NULL,
    long_name character varying(100) NOT NULL,
    rule_id character varying(20) NOT NULL,
    value_limit integer,
    rank integer NOT NULL,
    from_string character varying(20),
    from_concept_id integer,
    Constraint PK_categorization_function_parameters  PRIMARY KEY (extract_study_id, function_name, long_name, rule_id, rank)
);
    -- might want a key for when accessed by study_id, function_name, long_name, and rule_id  to get the relevant group;

drop table if exists categorization_function_qualifiers;
CREATE TABLE categorization_function_qualifiers (
    extract_study_id integer NOT NULL,
    function_name character varying(100) NOT NULL,
    long_name character varying(100) NOT NULL,
    rule_id character varying(20) NOT NULL,
    vocabulary_id character varying(100) NOT NULL,
    concept_code character varying(100) NOT NULL, -- vocabulary_concept_id character varying(100) NOT NULL,
    value_vocabulary_id character varying(100),
    value_as_string character varying(100),
    value_as_number integer,
    value_as_concept_id character varying(100),
    Constraint PK_categorization_function_qualifiers  PRIMARY KEY (extract_study_id, function_name, long_name, rule_id, vocabulary_id, concept_code)
);

-- should be renamed categorization_function_wide TODO
drop table if exists categorization_function_table;
CREATE TABLE categorization_function_table (
    extract_study_id integer,
    function_name character varying(100),
    long_name character varying(100),
    from_table character varying(100),
    from_column character varying(100),
    from_vocabulary_id character varying(100),
    from_concept_code character varying(100)
);


