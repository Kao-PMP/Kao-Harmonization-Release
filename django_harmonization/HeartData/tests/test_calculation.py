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

class CalculationTest(unittest.TestCase):
    def runTest(self):
        test()

    # from a->x, b->y, c->z
    def test(self):
        """ begrudingly requires a connection to a database that has the metadata in it
        """
        print("CalculationTest.test()...")
        self.assertEqual(1,1)

        ##calc = new CalculatedFieldFunction(con, 1, "best_bmi")
        ##calc.test()
        print("...CalculationTest.test()")
        


