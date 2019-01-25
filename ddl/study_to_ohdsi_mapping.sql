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


drop table if exists  study_to_ohdsi_mapping;
CREATE TABLE study_to_ohdsi_mapping (
    study_id integer NOT NULL,
    from_table character varying(100) NOT NULL,
    from_column character varying(100) NOT NULL,
    function_name character varying(100),
    vocabulary_id character varying(100), --vocabulary_name character varying(100),
    concept_code character varying(100), -- vocabulary_term_id character varying(100),
    to_table character varying(100),
    to_column character varying(100),
    addl_value_1 character varying(20),
    addl_column_1 character varying(20),
    from_where_clause character varying(100),
    comment character varying(250),
    from_where_column character varying(100),
    units character varying(20)
);

