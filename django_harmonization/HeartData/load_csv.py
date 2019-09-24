#!/usr/bin/env python3
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
 load.py <DBNAME> <SCHEMA> <FILENAME> <TABLENAME>
 Python Version: 3.6.3

 Reads csv files into postgres without the need for creating the table before hand.
 cribbed from https://stackoverflow.com/questions/2987433/how-to-import-csv-file-data-into-a-postgresql-table
   https://stackoverflow.com/questions/2987433/
   https://creativecommons.org/licenses/by-sa/3.0/
   https://stackoverflow.com/users/1779128/robinl

 This is research code for demonstration purposes only.

 croeder 6/2017 chris.roeder@ucdenver.edu


 Ex.: unix>load.py heart_2017-09-01 best foo.csv foo
 Ex.: unix>load.py heart_2017-09-01 hfaction foo.csv foo
'''

import sys
import pandas as pd
from sqlalchemy import create_engine

if __name__ == '__main__':

    print(sys.argv)
    DBNAME = sys.argv[1]
    SCHEMA = sys.argv[2]
    FILENAME = sys.argv[3]
    TABLENAME = sys.argv[4]
    USERNAME = sys.argv[5]
    PASSWORD = sys.argv[6]
    HOST = sys.argv[7]

    print("load_csv.py db:{}, schema:{}, file:{} table:{}, user:{} password:{} host:{}".format(DBNAME, SCHEMA, FILENAME, TABLENAME, USERNAME, PASSWORD, HOST))
    DF = pd.read_csv(FILENAME)
    DF.columns = [c.lower() for c in DF.columns] #postgres doesn't like capitals or spaces

    ENGINE = create_engine('postgresql://'+ USERNAME + ':' + PASSWORD + '@' + HOST + ':5432/' + DBNAME)

    DF.to_sql(TABLENAME, ENGINE, schema=SCHEMA)
