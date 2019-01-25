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


drop table if exists events_mapping;
CREATE TABLE  events_mapping (
	study_id int NOT NULL,
    from_table varchar(50),
    from_column varchar(50),
    to_table varchar(50),
    to_column varchar(50),
    value_vocabulary_id varchar(50),
    value_concept_code varchar(50),
    addl_column varchar(50),
    addl_value varchar(50),
    from_date_column varchar(50),
    where_clause varchar(256),
    Constraint PK_events_mapping  PRIMARY KEY (study_id, from_table, from_column, to_table, to_column, where_clause)
);

