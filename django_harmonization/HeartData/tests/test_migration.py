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
import psycopg2
from HeartData.migrate import migrate_by_mappings
from HeartData.migrate_functions import _lookup_concept_id
from HeartData.migrate_functions import map_number
from HeartData.migrate_functions import map_string
from HeartData.migrate_functions import not_null_number
from HeartData.migrate_functions import not_null
from HeartData.concepts import YES_CONCEPT_ID
from HeartData.concepts import NO_CONCEPT_ID
from HeartData.person import  TestPerson
from ui.models import  StudyMappingArguments
from django.test import TestCase

#class MigrationTest(unittest.TestCase):
class MigrationTest(TestCase):
    
    def setUp(self):
        # This only where in prod where we have that database.
        # The infuriating thing is that some of these tests use the concept table...
        db_name = 'heart_db_v3'
        user_name = 'christopherroeder'
        self.con = None
        ##self.con = psycopg2.connect(database=db_name, user=user_name) 
        ##self.con.autocommit=True;
        ##self.con.set_session(readonly=True)
        print("MigrationTest")

    # from a->x, b->y, c->z
    def test_convert_row(self):
        #print("MigrationTest.test_convert_row...")
        self.assertEqual(1,1)
        #print("...MigrationTest.test_convert_row")

# fails in BB pipeline
    def test_lookup_concept_id(self):
        if self.con:
            concept_id = _lookup_concept_id('SNOMED', '413491005', self.con)
            self.assertEqual(concept_id, 4211331)
# TODO
    def test_select_values(self):
        if self.con:
            #select_values(mapping, personObj, person_ids, value_cursor) :
             
            #Mapping has keys from_table, from_column, optionally from_where_clause, from_where_column, has_date
            mapping=[]
            mapping.append({'from_table':'X',  'from_column':'c', 'has_date':False})
            mapping.append({'from_table':'Xd', 'from_column':'c', 'has_date':True})
            mapping.append({'from_table':'Y',  'from_column':'c', 'from_where_clause':'x', 'from_where_column':'w', 'has_date':False})
            mapping.append({'from_table':'Yd', 'from_column':'c', 'from_where_clause':'x', 'from_where_column':'w', 'has_date':True})
            person_ids=[1,2]
            #personObj. 
            #value_cursor=  

    def test_map_number(self):
        if self.con:
            a1 = {'mapped_number':1, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'413491005'}  # 4211331
            a2 = { 'mapped_number':2, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'413582008'}  # 4211353
            a3 = { 'mapped_number':3, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'15086000'}  # 4035165
            a4 = { 'mapped_number':5, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'413773004'}  # 4185154
            a5 = { 'mapped_number':8, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'415226007'}   # 4190758
            arguments = [ a1, a2, a3, a4, a5 ]
            mapping = None
            self.assertEqual(map_number(1, mapping, arguments, self.con), 4211331)
            self.assertEqual(map_number(2, mapping, arguments, self.con), 4211353)
            self.assertEqual(map_number(3, mapping, arguments, self.con), 4035165)
            self.assertEqual(map_number(5, mapping, arguments, self.con), 4185154)
            self.assertEqual(map_number(8, mapping, arguments, self.con), 4190758)
            self.assertEqual(map_number(4, mapping, arguments, self.con), None)
            # text?
            self.assertEqual(map_number('c', mapping, arguments, self.con), None)
            self.assertEqual(map_number(None, mapping, arguments, self.con), None)
    
            # wtf? calling map_string with a number config produced  a crash here
            with self.assertRaisesMessage(KeyError, 'mapped_string'):
                map_string(2, mapping, arguments, self.con)
        
    def test_map_string(self):
        if self.con:
            a1 = {'mapped_string':'a', 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'413491005'}  # 4211331
            a2 = { 'mapped_string':'b', 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'413582008'}  # 4211353
            a3 = { 'mapped_string':'c', 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'15086000'}  # 4035165
            a4 = { 'mapped_string':'d', 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'413773004'}  # 4185154
            a5 = { 'mapped_string':'e', 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'415226007'}   # 4190758
            arguments = [ a1, a2, a3, a4, a5 ]
            mapping = None
            self.assertEqual(map_string('a', mapping, arguments, self.con), 4211331)
            self.assertEqual(map_string('b', mapping, arguments, self.con), 4211353)
            self.assertEqual(map_string('c', mapping, arguments, self.con), 4035165)
            self.assertEqual(map_string('d', mapping, arguments, self.con), 4185154)
            self.assertEqual(map_string('e', mapping, arguments, self.con), 4190758)
            self.assertEqual(map_string('foobar', mapping, arguments, self.con), None)
            self.assertEqual(map_string(None, mapping, arguments, self.con), None)
    
            # wtf? calling map_number with a string config produced  a crash here
            with self.assertRaisesMessage(KeyError, 'mapped_number'):
                map_number(2, mapping, arguments, self.con)
        
    #def map_number(value, mappings, arguments): 
    #    (_, number_value, _, map_target, _, _) 

    def test_not_null_number(self):
        print("test_not_null_number")
        if self.con:
            mapping_arguments = [ 
                {'mapped_number':-1, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373066005'},  # id 4188540 NO
                {'mapped_number': 0, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373066001'},  # id 4188539 YES   
                {'mapped_number': 1, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373067001'} ] # id 4188539 YES
            mapping = None
            print("test_not_null_numbers")
            self.assertEqual(not_null_number(None, mapping, mapping_arguments, self.con), NO_CONCEPT_ID)
            self.assertEqual(not_null_number(0, mapping, mapping_arguments, self.con),  YES_CONCEPT_ID)
            self.assertEqual(not_null_number(1, mapping, mapping_arguments, self.con),  YES_CONCEPT_ID)
            self.assertEqual(not_null_number(-1, mapping, mapping_arguments, self.con),  YES_CONCEPT_ID)
    
            with self.assertRaisesMessage(KeyError, 'mapped_string'):
                map_string(2, mapping, arguments, self.con)
        print("test_not_null_number fini")

    def test_not_null_number_2(self):
        print("test_not_null_number_2")
        if self.con:
            arguments = [ 
                {'mapped_number':-1, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373066001'},  # id 4188539 YES
                {'mapped_number': 0, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373067005'},   
                {'mapped_number': 1, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373067005'} ]  # id 4188540 NO
            mapping = None
            self.assertEqual(not_null_number(None, mapping, arguments, self.con), YES_CONCEPT_ID)
            self.assertEqual(not_null_number(0, mapping, arguments, self.con),  NO_CONCEPT_ID)
            self.assertEqual(not_null_number(1, mapping, arguments, self.con),  NO_CONCEPT_ID)
        print("test_not_null_number-2 fini")

    def test_not_null(self):
        self.assertEqual(not_null(1, None, None, None),    YES_CONCEPT_ID)
        self.assertEqual(not_null(0, None, None, None),    YES_CONCEPT_ID)
        self.assertEqual(not_null(-1, None, None, None),   YES_CONCEPT_ID)
        self.assertEqual(not_null(None, None, None, None),  NO_CONCEPT_ID)


#    def test_migrate_by_mappings(self):
#        personObj = TestPerson(1)
#        person_ids=[1,2]
#        mapping_arguments = [ 
#                {'mapped_number':-1, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373066005'},  # id 4188540 NO
#                {'mapped_number': 0, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373066001'},  # id 4188539 YES   
#                {'mapped_number': 1, 'to_concept_vocabulary_id':'SNOMED', 'to_concept_code':'373067001'} ] # id 4188539 YES
#        migrate_by_mappings(self.con, mapping_arguments, 1, personObj, person_ids)
#
#
