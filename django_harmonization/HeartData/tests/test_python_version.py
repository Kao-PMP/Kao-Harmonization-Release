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


 
import sys
from django.test import TestCase

class PytonVersionTest(TestCase):
    def setUp(self):
        print("test_python_versionn.setup()")

    def runTest(self):
        #print(sys.version)
        #self.assertTrue('3.5.1' == sys.version[:5] or '3.6.3' == sys.version[:5] or ')
        self.assertTrue('3' == sys.version[:1])


