'''
   Copyright 2017 The Regents of the University of Colorado

   Licensed under the Apache License, Version 2.0 (the "License")
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
''' 
 observation entity
 Python Version: 3.6.3

 croeder 7/2017 chris.roeder@ucdenver.edu
'''

import psycopg2.extras
import logging

logger = logging.getLogger(__name__)

def fetch(con, ohdsi_table, person_id,  vocabulary_id, concept_id):
    if (ohdsi_table == 'observation') :
        return _fetch_observation(con, person_id, vocabulary_id, concept_id)
    elif (ohdsi_table == 'measurement') :
        return _fetch_measurement(con, person_id, vocabulary_id, concept_id)
    else:
        logger.error("observation.fetch() uknown table:%s", ohdsi_table)
    

def _fetch_observation(con, person_id,  vocabulary_id, concept_id):
    """ ...does not take a date as an argument, so it returns whatever dates is has for that patient/term
        returns (number, string, concept, date)
    """
    stmt = ("SELECT value_as_number, value_as_string, value_as_concept_id, o.observation_date"
            "  FROM observation o, concept c "
            " WHERE c.concept_code = %s"
            "   AND c.vocabulary_id = %s"
            "   AND c.concept_id = o.observation_concept_id"
            "   AND  o.person_id = %s  "
            " ORDER BY o.observation_date ASC")
    cur = con.cursor()
    cur.execute(stmt,  (concept_id, vocabulary_id, person_id))
    ohdsi_rows = cur.fetchall()
    if (len(ohdsi_rows) < 1) :
        logger.debug("observation.py _fetch_observation() got nothing person:%s, vocab:%s, term:%s", person_id, vocabulary_id, concept_id)
        logger.debug("  observation.py _fetch_observation() stmt:%s", stmt)
    return  ohdsi_rows

def _fetch_measurement(con, person_id,  vocabulary_id, concept_id):
    """ ...does not take a date as an argument, so it returns whatever dates is has for that patient/term
        returns ((number, string, concept), date)
    """
    stmt = ("SELECT value_as_number,  null,  value_as_concept_id, m.measurement_date"
            "  FROM measurement m, concept c "
            " WHERE c.concept_code = %s"
            "   AND c.vocabulary_id = %s"
            "   AND c.concept_id = m.measurement_concept_id"
            "   AND  m.person_id = %s"
            " ORDER BY m.measurement_date ASC")
    cur = con.cursor()
    cur.execute(stmt,  (concept_id, vocabulary_id, person_id))
    ohdsi_rows = cur.fetchall()
    if (len(ohdsi_rows) < 1) :
        logger.debug("observation.py _fetch_measurement() got nothing person:%s, vocab:%s, term:%s", person_id, vocabulary_id, concept_id)
        logger.debug("  observation.py _fetch_measurement() stmt:%s", stmt)
    return  ohdsi_rows

