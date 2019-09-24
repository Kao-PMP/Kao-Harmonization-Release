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


from django.test import TestCase
import HeartData.extract


class ExtractTest(TestCase):


    # in the style returned by ObservationServices.fetch(con, person_id, vocabulary_id, concept_id)
    # tests  = [ (name, input, output) ]  input is a person_values, output is a different form of same
    #   input  = {(vocab, concept): { date: value,..}} 
    #   output = [ {(vocab, concept): value } ]
    flatten_values_tests = [
        (
            "basic",             
            #{  ("v1", "c1"):  {"2017-07-01": "7", "2017-07-04": "6",  "2017-06-01": "5"}  },
            # the database call has an "order by" clause...
            {  ("v1", "c1"):  {"2017-06-01": "5", "2017-07-01": "7", "2017-07-04": "6"}  },
            {  ("v1", "c1"): "5"}
        ),
        (
            "epoch end", 
            {("v5", "c5"):{"2038-01-20":"2"}},
            {("v5", "c5"):"2"}
        ),
        (
            "epoch end 2", 
            {("v5", "c5"):{"2035-01-20":"2"}},
            {("v5", "c5"):"2"}
        ),
        (
            "past and future 2",
            { ("v2", "c2"):  { "2010-07-01":"7", "2011-07-02":"9", "2011-07-03":"8", "2007-07-04":"6", "2020-06-01":"5"  } },
            { ("v2", "c2"):  "7"}
        ),
        (
            "past and future 1",
            { ("v2", "c2"):  { "2010-07-01":"7", "2011-07-02":"9", "2011-07-03":"8", "2007-07-04":"6", "2038-06-01":"5"  } },
            { ("v2", "c2"):  "7"}
        ),
        (
            "past and future 3",
            { ("v2", "c2"):  { "2010-07-01":"7", "2011-07-02":"9", "2011-07-03":"8", "2007-07-04":"6", "2035-06-01":"5"  } },
            { ("v2", "c2"):  "7"}
        ),
        (
            "empty", 
            {("v3", "c3"):{}},
            {("v3", "c3"):None}
        ),
        (
            "single", 
            {("v4", "c4"):{"2017-07-02":"1"}},
            {("v4", "c4"):"1"}
        ),
        (
            "two backwards",
            {("v6", "c6"):{"2017-07-02":"9", "2017-07-03":"8"}},
            {("v6", "c6"):"9"}
        ),
        (
            "two forwards",
            {("v7", "c7"):{ "2017-07-03":"8", "2017-07-22":"9"}},
            {("v7", "c7"):"8"}
        ),
        (
            "realistic", # has many terms for a single person
            {
                ("v5", "c5"):{"2038-01-20":"2"},
                ("v6", "c6"):{"2017-07-02":"9", "2017-07-03":"8"},
                ("v7", "c7"):{"2017-07-03":"8", "2017-07-22":"9"},
                ("v3", "c3"):{}
            },
            {
                ("v3", "c3"):None,
                ("v5", "c5"):"2",
                ("v6", "c6"):"9",
                ("v7", "c7"):"8",
            }
        )
    ]
        

    def setUp(self):
        print("setup...")

    def _testPrintFlattenValuesData(self): # FIX nothing but prints here!!
        """ scaffolding: used in dev to check the test value data structure """
        #print("ExtractTest. Test Data for testFlattenDate...")
        #for (name, input, output)  in ExtractTest.flatten_values_tests:
            #print("name:", name)

            #print("  input:")
            #for (key, value) in input.iteritems():
                #print("    key:", key)
                #print("      value:", value)

            #print("  expected output:")
            #for (key, value) in output.iteritems():
                #print("    key:", key)
                #print("      value:", value)
        #print("...Test Data for testFlattenDate")

    def testFlattenValue(self):
        #print("ExtractTest testFlattenValue...")
        #extract_object = extract.Extract(None)
        extract_object = HeartData.extract.Extract(None)
        for (name, input, expected_output)  in ExtractTest.flatten_values_tests:
            real_output = extract_object.flatten_person_values(input, 1)
            if (real_output != expected_output) :
                #print("  FAILED", name)
                #print("  input:", input, name)
                self.assertEqual(real_output, expected_output)
            #else:
                #print("  PASSED", name)

        #print("...testFlattenValue")

    def tearDown(self):
        print("...tearDown")


            
