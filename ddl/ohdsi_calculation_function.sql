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

drop table if exists ohdsi_calculation_function;

CREATE TABLE ohdsi_calculation_function (
    study_id integer NOT NULL,
    function_name character varying(100) NOT NULL,
    to_vocabulary_id character varying(100) NOT NULL, -- to_vocabulary_name character varying(100) NOT NULL,
    to_concept_code character varying(100) NOT NULL, -- to_term_id character varying(100) NOT NULL,
    to_table character varying(100),
    to_column character varying(100)
    Constraint PK_ohdsi_calculated_fields  PRIMARY KEY (study_id, function_name) 
);


