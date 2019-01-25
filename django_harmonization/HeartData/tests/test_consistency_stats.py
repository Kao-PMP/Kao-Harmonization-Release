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
import consistency_stats

class CalculationTest(unittest.TestCase):
    def runTest(self):
        test()

    # from a->x, b->y, c->z
    def test(self):
        """ requires a connection to a database that has the metadata in it
        """
        print("CalculationTest.test()...")
        self.assertEqual(1,1)

        ##calc = new CalculatedFieldFunction(con, 1, "best_bmi")
        ##calc.test()
        print("...CalculationTest.test()")


    def test_calculate_median(self):
        print("CalculationTest.test_calculate_median()...")
        tests = []
        answers = []

        tests.append({1:100,2:100,3:100})
        answers.append(2)

        tests.append({1:100,2:100,3:10})
        answers.append(2)

        tests.append({1:10,2:100,3:100})
        answers.append(2)

        tests.append({1:10,2:10,3:100})
        answers.append(3)

        tests.append({1:100,2:10,3:10})
        answers.append(1)

        tests.append({1:0,2:10,3:10})
        answers.append(2)

        tests.append({1:10,2:10,3:0})
        answers.append(1)

        for i in range(0,len(tests)):
            num  =  consistency_stats._num_values_in_freq_dist(tests[i])
            a = consistency_stats.calculate_median(tests[i], num)
            if a != answers[i]:
                print("  failed test_calculate_median() test ", i, " failed" , tests[i], answers[i], "got: ", a)
            else:
                print("  passed", i, tests[i])

            self.assertEqual(a, answers[i])
        print("...CalculationTest.test_calculate_median()")
