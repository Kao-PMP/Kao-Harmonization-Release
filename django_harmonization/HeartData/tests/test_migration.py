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


 
import unittest

class MigrationTest(unittest.TestCase):
    def runTest(self):
        test_convert_row()
        test_select_values()

    # from a->x, b->y, c->z
    def test_convert_row(self):
        print("MigrationTest.test_convert_row...")
        self.assertEqual(1,1)
        print("...MigrationTest.test_convert_row")


    def test_select_values(self):
        #select_values(mapping, personObj, person_ids, value_cursor) :
         
        #Mapping has keys from_table, from_column, optionally from_where_clause, from_where_column, has_date
        mapping=[]
        mapping[0]={'from_table':'X',  'from_column':'c', 'has_date':false}
        mapping[1]={'from_table':'Xd', 'from_column':'c', 'has_date':true}
        mapping[2]={'from_table':'Y',  'from_column':'c', 'from_where_clause':'x', 'from_where_column':'w', 'has_date':false}
        mapping[3]={'from_table':'Yd', 'from_column':'c', 'from_where_clause':'x', 'from_where_column':'w', 'has_date':true}
        person_ids=[1,2]
        personObj. 
        value_cursor=  

#def migrate_by_mappings(con, mappings, observation_number_start, personObj, person_ids):


