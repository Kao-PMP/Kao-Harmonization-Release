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
 entity/study
 Python Version: 3.6.3

 functions (despite the entity directory) to  access to the study table

 croeder 11/2017 chris.roeder@ucdenver.edu
'''

def get_study_name(con, study_id) :
    cur = con.cursor()
    stmt = "SELECT study_name FROM study WHERE study_id = %s"
    print(type(study_id))
    print(study_id)
    cur.execute(stmt, (study_id, ))
    rows = cur.fetchall()
    cur.close()
    if (len(rows)>0):
        return rows[0][0]
    else:
        raise ValueError("no match for study id", name)

def get_study_details(con, name) :
    ''' returns (study_id, observation_range_start, observation_range_end, person_id_range_start, person_id_range_end ) given a study name
        raises if it can't find the study name
    ''' 
    cur = con.cursor()
    stmt = "SELECT study_id, observation_range_start, observation_range_end, person_id_range_start, person_id_range_end FROM study WHERE study_name = %s"
    cur.execute(stmt, (name,))
    rows = cur.fetchall()
    cur.close()
    if (len(rows)>0):
        return (rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4])
    else:
        raise ValueError("no match for study name", name)
        
