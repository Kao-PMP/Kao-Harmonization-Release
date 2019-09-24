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
import HeartData.consistency_stats

class CalculationTest(TestCase):
    def runTest(self):
        test()

    # from a->x, b->y, c->z
    def test(self):
        """ requires a connection to a database that has the metadata in it
        """
        #print("CalculationTest.test()...")
        self.assertEqual(1,1)

        ##calc = new CalculatedFieldFunction(con, 1, "best_bmi")
        ##calc.test()
        #print("...CalculationTest.test()")

    def test_convert_freq_dist_to_flat_list(self):
        #print("CalculationTest.test_convert_freq_dist_to_flat_list()..")

        fd_map={1:10}
        flat_list=[1,1, 1,1,1, 1,1, 1,1,1] 
        retval = HeartData.consistency_stats.convert_freq_dist_to_flat_list(fd_map)
        self.assertEqual(flat_list, retval)

        fd_map={1:0}
        flat_list=[] 
        retval = HeartData.consistency_stats.convert_freq_dist_to_flat_list(fd_map)
        self.assertEqual(flat_list, retval)

        fd_map={1:1}
        flat_list=[1] 
        retval = HeartData.consistency_stats.convert_freq_dist_to_flat_list(fd_map)
        self.assertEqual(flat_list, retval)

        fd_map={1:2}
        flat_list=[1,1] 
        retval = HeartData.consistency_stats.convert_freq_dist_to_flat_list(fd_map)
        self.assertEqual(flat_list, retval)

        fd_map={1:1, 2:1, 3:1}
        flat_list=[1,2,3] 
        retval = HeartData.consistency_stats.convert_freq_dist_to_flat_list(fd_map)
        self.assertEqual(flat_list, retval)

        fd_map={1:2, 2:3, 3:4}
        flat_list=[1,1, 2,2,2, 3,3,3,3] 
        retval = HeartData.consistency_stats.convert_freq_dist_to_flat_list(fd_map)
        self.assertEqual(flat_list, retval)

    def test_calculate_median(self):
        self.assertEqual(None, HeartData.consistency_stats.calculate_median([]))
        self.assertEqual(1, HeartData.consistency_stats.calculate_median([1]))
        self.assertEqual(4.5, HeartData.consistency_stats.calculate_median([0,9]))
        self.assertEqual(9, HeartData.consistency_stats.calculate_median([0,9,18]))

    def test_calculate_median_from_freq_dist(self):
        #print("CalculationTest.test_calculate_median()...")
        tests = []
        answers = []

        tests.append({1:100,2:100,3:100})
        answers.append(2)

        tests.append({1:100,2:100,3:100, 4:100})
        answers.append(2.5)

        tests.append({1:100,2:100,3:100, 4:10})
        answers.append(2)

        tests.append({1:100,2:100,3:10})
        answers.append(2)

        tests.append({1:100,2:100,3:10, 4:5})
        answers.append(2)

        tests.append({1:10,2:100,3:100})
        answers.append(2)

        tests.append({1:10,2:100,3:100, 4:110})
        answers.append(3)

        tests.append({1:10,2:10,3:100})
        answers.append(3)

        tests.append({1:100,2:10,3:10})
        answers.append(1)

        tests.append({1:0,2:10,3:10})
        answers.append(2.5)

        tests.append({1:10,2:10,3:0})
        answers.append(1.5)

        for i in range(0, len(tests) -1): # FIX  nothing but prints here
            a = HeartData.consistency_stats.calculate_median_from_freq_dist(tests[i])
            #if a != answers[i]:
                #print("  failed test_calculate_median() test ", i, " failed" , tests[i], answers[i], "got: ", a)
            #else:
                #print("  passed", i, tests[i])

            self.assertEqual(a, answers[i], str(a) + ' ' + str(i) + ' ' + str(answers[i]) )
        #print("...CalculationTest.test_calculate_median()")
