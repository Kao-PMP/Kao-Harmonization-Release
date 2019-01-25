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
import sqlite3
import tempfile
import categorization
import psycopg2

## python -m unittest discover tests
## python -m unittest -v tests/test_categorization.py 

class CategorizationTest(unittest.TestCase):

    # column_d and column_e are configured to test/show how the descending and ascending
    # rules deal with < or <= etc.
    # d: 100, 80, 60 means: >100, <=100 & >80, <=80 & > 60, <= 60
    #   or  > 100, 100-81, 80-61, <= 60
    #   or > 100, > 80, > 60, remainder in that order.
    #
    # e: 60, 80, 100 means <=60, 61-80, 81-100, > 100
    #  or <=60, <=80, <=100, remainder

    # need an additional field to distinguish different qualifiers on the same
    # rule applied to the same field
    metadata = [
        ("1", "ranges_to_rank_asc",  "column_a", "first-rule",  "LOINC", "12345-6"),
        ("1", "ranges_to_rank_asc",  "column_a", "second-rule", "LOINC", "12345-6"),
        ("1", "ranges_to_rank_desc", "column_d", "a0",          "LOINC", "12345-0"),
        ("1", "ranges_to_rank_asc",  "column_b", "first-b-rule","LOINC", "98765-0"),
        ("1", "ranges_to_rank_asc",  "column_e", "a1",          "LOINC", "12345-1"),
        ("1", "ranges_to_rank_desc", "column_f", "a2",          "LOINC", "98765-1"),

        # trouble, no matching paramters. Check this error condition works correctly
        ##("1", "ranges_to_rank_asc", "column_c", "trouble",  "LOINC", "98765-0")
        ]

    parameters = [
        [1, "ranges_to_rank_asc", "column_a", "first-rule", 10, 1],
        [1, "ranges_to_rank_asc", "column_a", "first-rule", 20, 2],
        [1, "ranges_to_rank_asc", "column_a", "first-rule", 30, 3],
        [1, "ranges_to_rank_asc", "column_a", "first-rule", None, 4],

        [1, "ranges_to_rank_desc", "column_d", "a0",  100, 1],
        [1, "ranges_to_rank_desc", "column_d", "a0",   80, 2],
        [1, "ranges_to_rank_desc", "column_d", "a0",   60, 3],
        [1, "ranges_to_rank_desc", "column_d", "a0", None, 4],

        [1, "ranges_to_rank_asc", "column_e", "a1",   60, 1],
        [1, "ranges_to_rank_asc", "column_e", "a1",   80, 2],
        [1, "ranges_to_rank_asc", "column_e", "a1",  100, 3],
        [1, "ranges_to_rank_asc", "column_e", "a1", None, 4],

        # note inverted order
        [1, "ranges_to_rank_asc", "column_a", "second-rule", 21, 3],
        [1, "ranges_to_rank_asc", "column_a", "second-rule", 14, 2],
        [1, "ranges_to_rank_asc", "column_a", "second-rule", 7, 1],
        [1, "ranges_to_rank_asc", "column_a", "second-rule", None, 4],

        [1, "ranges_to_rank_asc", "column_b", "first-b-rule", 100, 1],
        [1, "ranges_to_rank_asc", "column_b", "first-b-rule", None, 2],

        [1, "ranges_to_rank_desc", "column_f", "a2", 100, 1],
        [1, "ranges_to_rank_desc", "column_f", "a2", None, 2],
        ]

    qualifiers = [
        # male
        [1, "ranges_to_rank_asc", "column_a", "first-rule",  "LOINC", "9999-1", "LOINC", "8881-1", None, None],
        # female
        [1, "ranges_to_rank_asc", "column_a", "second-rule", "LOINC", "9999-1", "LOINC", "8881-2", None, None]
        # no entry, no qualifiers on column_b
        ]

    # number, string, concept_id
    person_values = [ #0
        { (u"LOINC", u"12345-6") : ( 9, 'x', 999), 
          (u"LOINC", u"12345-0") :(101, 'x', 999), 
          (u"LOINC", u"12345-1") :(59, 'x', 999), 
          (u"LOINC", u"9999-1")  : ( 1, 'x', u"8881-1"), 
          (u"LOINC", u"98765-0") : (99, 'x', 999),
          (u"LOINC", u"98765-1") : (99, 'x', 999)  
        }, # 1
        { (u"LOINC", u"12345-6") : (19, 'x', 999), 
          (u"LOINC", u"12345-0") :(100, 'x', 999), 
          (u"LOINC", u"12345-1") :( 60, 'x', 999), 
          (u"LOINC", u"9999-1")  : ( 1, 'x', u"8881-1"), 
          (u"LOINC", u"98765-0") :(110, 'x', 999), 
          (u"LOINC", u"98765-1") :(110, 'x', 999) 
        }, #  2
        { (u"LOINC", u"12345-6") : (29, 'x', 999), 
          (u"LOINC", u"12345-0") : (99, 'x', 999), 
          (u"LOINC", u"12345-1") :( 61, 'x', 999), 
          (u"LOINC", u"9999-1")  : ( 1, 'x', u"8881-1"), 
          (u"LOINC", u"98765-0") : (99, 'x', 999),  
          (u"LOINC", u"98765-1") : (99, 'x', 999)  
        }, # 3
        { (u"LOINC", u"12345-6") : (31, 'x', 999), 
          (u"LOINC", u"12345-0") : (81, 'x', 999), 
          (u"LOINC", u"12345-1") :( 99, 'x', 999), 
          (u"LOINC", u"9999-1")  : ( 1, 'x', u"8881-1"), 
          (u"LOINC", u"98765-0") : (99, 'x', 999),  
          (u"LOINC", u"98765-1") : (99, 'x', 999)  
        }, # 4
        { (u"LOINC", u"12345-6") : (10, 'x', 999), 
          (u"LOINC", u"12345-0") : (80, 'x', 999), 
          (u"LOINC", u"12345-1") :(100, 'x', 999), 
          (u"LOINC", u"9999-1")  : ( 1, 'x', u"8881-2"), 
          (u"LOINC", u"98765-0") : (99, 'x', 999),
          (u"LOINC", u"98765-1") : (99, 'x', 999)  
        }, # 5
        { (u"LOINC", u"12345-6") : (13, 'x', 999), 
          (u"LOINC", u"12345-0") : (79, 'x', 999), 
          (u"LOINC", u"12345-1") :(101, 'x', 999), 
          (u"LOINC", u"9999-1")  : ( 1, 'x', u"8881-2"), 
          (u"LOINC", u"98765-0") : (99, 'x', 999),  
          (u"LOINC", u"98765-1") : (99, 'x', 999)  
        }, # 6
        { (u"LOINC", u"12345-6") : (20, 'x', 999), 
          (u"LOINC", u"12345-0") : (61, 'x', 999), 
          (u"LOINC", u"12345-1") :( 80, 'x', 999), 
          (u"LOINC", u"9999-1")  : ( 1, 'x', u"8881-2"), 
          (u"LOINC", u"98765-0") :(101, 'x', 999), 
          (u"LOINC", u"98765-1") :(101, 'x', 999)  
        }, # 7
        { (u"LOINC", u"12345-6") : (22, 'x', 999), 
          (u"LOINC", u"12345-0") : (60, 'x', 999), 
          (u"LOINC", u"12345-1") :( 79, 'x', 999), 
          (u"LOINC", u"9999-1")  : ( 1, 'x', u"8881-2"), 
          (u"LOINC", u"98765-0") :(100, 'x', 999),  
          (u"LOINC", u"98765-1") :(100, 'x', 999)  
        }
        ]

    # for each rule, have an answer for each person 
    person_answers = [
        [None, None, None, None, None, None, None, None], # 12345-6 first
        [None, None, None, None, None, None, None, None], # 12345-6 first
        [1, 2,  1,  1,  1,  1,  2,   1], # 98765-0  
        [1, 2, 2, 2, 3, 3, 3, 4], # 12345-1
        [1, 1, 2, 3, 3, 4, 2, 2], # 12345-1
        [2, 1, 2, 2, 2, 2, 1, 2], # 98765-1 
    ]
#    person_answers = [
#        # 12345-6 
#        ##[None, None, None, None, None, None, None, None],
#
#        #12345-6 
#        ##[None, None, None, None, None, None, None, None],
#
#        #12345-0  # works on its own
#        [1, 2, 2, 2, 3, 3, 3, 4],
#
#        #98765-0 
#        #99, 110, 99, 99, 99, 99, 101, 100,
#        #[ 1,   2,  1,  1,  1,  1,  2,   1],
#        ##[ 1,   1,  1,  1,  1,  1,  1,   1],
#
#        #12345-1,
#        [1, 1, 2, 3, 3, 4, 2, 2],
#    ]

    def testSetup(self):
        """ just checks to see that the db got created with data inserted """
        # TODO get real
        print("CategorizationTest.checking setup...")
        cursor = self._con.cursor()
        #print("METADATA")
        cursor.execute("select * from categorization_function_metadata")
        rows = cursor.fetchall()
        #for row in rows:
        #    print(row)

        #print("PARAMETERS")
        cursor.execute("select * from categorization_function_parameters")
        rows = cursor.fetchall()
        #for row in rows:
        #    print(row)

        #print("QUALIFIERS")
        cursor.execute("select * from  categorization_function_qualifiers")
        rows = cursor.fetchall()
        #for row in rows:
        #    print(row)

        cursor.close()

        self.assertEqual(1,1)
        print("...CategorizationTest.checking setup")

#    def testLoad(self):
#        """ loads and prints the rules, needs for real assertions TODO """
#        print("TestCategorization.check load...")
#        rule_dict = categorization.CategorizationRule.load_rules(self._con, 1)
#        #for (column_id, rule_list) in rule_dict.items():
#        #    for rule in rule_list:
#        #        print(column_id, "rule", str(rule))
#        print("...check load")

    def setUp(self):
        print("TestCategorization.setup()")
        self._db_file = tempfile.NamedTemporaryFile(suffix='.sqlite')
        self._con = sqlite3.connect(self._db_file.name)
        cursor = self._con.cursor()
        # DDL
        ddl_file = open('../ddl/categorization.sql', 'r')
        ddl = ddl_file.read()
        statements=ddl.split(";")
        for stmt in statements:
            try:
                self._con.execute(stmt)
            except Exception as e:
                print(e)
                print("error:", stmt)


        # DATA - metadata
        stmt = ("insert into categorization_function_metadata "
                "(extract_study_id, function_name, long_name, rule_id, "
                "from_vocabulary_id, from_concept_code) "
                "values (  ?,  ?,  ?,  ?,  ?,  ?);") # sqlite
        for m in CategorizationTest.metadata:
            cursor.execute(stmt, m);

        # DATA - parameters
        stmt = ("insert into categorization_function_parameters "
                "(extract_study_id, function_name, long_name, rule_id, value_limit, rank) "
                "values ( ?,  ?,  ?,  ?,  ?, ?);")
        for p in CategorizationTest.parameters:
            cursor.execute(stmt, p);

        # DATA - qualifiers
        stmt = ("insert into categorization_function_qualifiers "
                "(extract_study_id, function_name, long_name, rule_id, "
                "vocabulary_id, concept_code, value_vocabulary_id, "
                "value_as_string, value_as_number, value_as_concept_id) "
                "values ( ?,  ?,  ?,  ?,  ?,  ?,  ?,  ?,  ?,  ?);")
        for q in CategorizationTest.qualifiers:
            cursor.execute(stmt, q);

        cursor.close()


#    def testLoad(self):
#        print("TestCategorization.loadTest...")
#        rule_dict = categorization.CategorizationRule.load_rules(self._con, 1)
#        #for (column, rules_list) in rule_dict.items():
#        #    for rule in rules_list:
#        #        print(column, rule)
#
#        self.assertEqual(1,1)
#        # TODO anyway to make this a reall asserted test?
#        print("...loadTest")

    def testApply(self):
        print("TestCategorization.applyTest...APPLY")
        rule_dict = categorization.CategorizationRule.load_rules(self._con, 1)
        rule_index=0
        for (column, rules_list) in rule_dict.items():
            print("COLUMN:", column)
            for rule in rules_list:
                person_index = 0
                for value_dict in CategorizationTest.person_values:
                    print("\nRULE:", rule_index, " person:", person_index, "\n   rule:", str(rule),
                            "\n   person:", value_dict)
                    if (rule.qualify(value_dict)):
                        test_val =  rule.apply(value_dict)
                        correct_val = CategorizationTest.person_answers[rule_index][person_index]
                        msg = str(rule) + " pid:" +str(person_index) + " \ndict:" + str(value_dict) \
                                        + " \nretval:" + str(test_val) + " n\npidx:" \
                                        + str(person_index) + " \nruleidx:" + str(rule_index)
                        print("expecting:", correct_val, " got ", test_val)
                        self.assertEqual(test_val, correct_val, msg)
                    person_index += 1
                rule_index += 1
        print("...applyTest APPLY")

#    def testQualify(self):
#        print("TestCategorization.qualifyTest...")
#        rule_dict = categorization.CategorizationRule.load_rules(self._con, 1)
#        for (column, rules_list) in rule_dict.items():
#            for rule in rules_list:
#                for value_dict in CategorizationTest.person_values:
#                    if rule.qualify(value_dict):
#                        ##print("qualifies:", value_dict)
#                        print("qualified:", rule)
#                    if not rule.qualify(value_dict):
#                        #print("    fails:", value_dict)
#                        print("Failes to Qualify:", rule)
#                        #print("")
#        # TODO put a real assert in here
#        print("...qualifyTest")
#
# 
#        self.assertEqual(1,1)

    # oh the dependencies! (on the database instance)
#    def test_fix_substitution_mark_psycopg(self):
#        con = psycopg2.connect(database="best", user="christopherroeder")
#        cursor = con.cursor()
#        stmt = "yak yak %s yak %s yak yak"
#        expected = "yak yak %s yak %s yak yak"
#        stmt2 = categorization.CategorizationRule._fix_substitution_mark(stmt, cursor)
#        self.assertEqual(stmt2, expected)
#
#    def test_fix_substitution_mark_sqlite(self):
#        self._db_file = tempfile.NamedTemporaryFile(suffix='.sqlite')
#        con = sqlite3.connect(self._db_file.name)
#        cursor = con.cursor()
#        stmt = "yak yak %s yak %s yak yak"
#        expected = "yak yak ? yak ? yak yak"
#        stmt2 = categorization.CategorizationRule._fix_substitution_mark(stmt, cursor)
#        self.assertEqual(stmt2, expected)

    def tearDown(self):
        self._con.close()

if __name__ == '__main__':
    unittest.main()

