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
 create index idx_observation_id_person_date on observation(observation_id, person_id, observation_date);
 create index idx_measurement_id_person_date on measurement(measurement_id, person_id, measurement_date);
create index idx_concept_code_vocab on concept (concept_code, vocabulary_id);
