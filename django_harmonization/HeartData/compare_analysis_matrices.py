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
 columns.py
 Python Version: 3.6.3
    
 This is research code for demonstration purposes only.

 croeder 7/2017 chris.roeder@ucdenver.edu
'''

import pandas
import re

if __name__ == '__main__':
    
    map = pandas.read_csv('both', delimiter=',', skipinitialspace=True)
    dave = pandas.read_csv('phenotypeset.csv', delimiter=',', skipinitialspace=True)
    chris = pandas.read_csv('paradigm.csv', delimiter=',', skipinitialspace=True)
    
    
    #access rows of a column by index:
    #for i in dave.index:
    #    print dave['patientid'][i] # works
    
    #for map_index in map.index:
    #    chris_column_number =  int(map['chris'][map_index]) -1
    #    dave_column_number =  int(map['column'][map_index])
    #    chris_column_name = chris.columns[int(chris_column_number)]
    #    dave_column_name = dave.columns[int(dave_column_number)]
    #    print map_index, chris_column_number, chris_column_name, dave_column_number, dave_column_name
    #
    #exit
    
    for map_index in map.index:
        chris_column_number =  int(map['chris'][map_index]) -1
        dave_column_number =  int(map['column'][map_index])
        chris_column_name = chris.columns[int(chris_column_number)]
        dave_column_name = dave.columns[int(dave_column_number)]
        error_count = 0
        for i in chris.index:
            aid = chris['AID'][i] 
            aid = re.sub(r'\'', '', aid)
            chris_value = chris[chris_column_name][i]
            #print 'CHRIS',i, aid,  chris_value
            dave_row = dave.loc[dave['patientid'] == aid]
            #print "DAVE:", dave_row[dave_column_number]
            #print "DAVE:", dave_column_number, "-->", dave_row[dave_column_name].values[0] 
            dave_value = dave_row[dave_column_name].values[0] # ouch!
            if chris_value != None and chris_value != dave_value :
                print("    ", aid, chris_column_name, chris_value, dave_column_name, dave_value)
                error_count += 1
    
        #if error_count > 0 and error_count < 6000:
        print map_index, chris_column_number, chris_column_name, dave_column_number, dave_column_name, "error_count:", error_count
    

# access columns of a row by column name and index
#for c in dave.columns:
#    print dave[c][2]

# access a row by a value of a column (select, locate)
#for i in chris.index:
#    aid =  chris['AID'][i]
#    print i, aid
#    print "x", aid, dave.loc[dave['patientid'] == aid]




