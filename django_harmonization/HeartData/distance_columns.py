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
 distance_columns.py
 Python Version: 3.6.3

 find a column that is very similar to others

 This is research code for demonstration purposes only.

 croeder 10/2017 chris.roeder@ucdenver.edu
'''

# progression of ideas
# - edit distance max and average over 2708 subjects
# - % same value
# - independant ==> p(a) = p(a|b) TODO


import sys
import csv
from collections import defaultdict

def _get_matrix(file_name):
    """ Trims header row and id column (1st of each) """
    # return reader[1:][1:]

    header = None
    with  open(file_name, "r") as file:
        matrix = []
        reader = csv.reader(file)
        for string_row in reader:
            number_row=[]
            if header == None:
                header = string_row
                header.append("    xx")
            else:
                for s in string_row:
                    s = s.strip()
                    if s == "NA":
                        number_row.append(None) 
                    else:
                        number_row.append(float(s)) 
                number_row.append(number_row[20])

            matrix.append(number_row)
        # add in a test case that is identical ...
        return (header, matrix)

def _edit_distance(index_a, index_b, matrix):
    c_sum=0
    c_max=0
    c_min=sys.maxsize
    equal_count=0
    distance=0
    col_a = []
    col_b = []
    for row in matrix:
        col_a.append(row[index_a])
        col_b.append(row[index_b])
        if row[index_a] != None and row[index_b] != None:
            distance = abs(row[index_a] - row[index_b])
            c_sum += distance
            if distance > c_max:
                c_max = distance
            if distance < c_min:
                c_min = distance
            if distance == 0:
                equal_count += 1

    return (c_min, c_sum/float(len(matrix)), c_max, equal_count)

def _show_column_differences(i,j, matrix, header):
    print(i,":", end='')
    count=0
    for row in matrix:
        if row[i] != row[j]:
            #print row[i], row[j]
            count += 1
    print((i,j), (header[i+1], header[j+1]), "-->", count, end='')
 
def _min_column_difference(j, matrix):
    min_avg=sys.maxsize
    min_avg_index=0
    min_max=sys.maxsize
    min_max_index=0
    for i in range(j, len(matrix[1])):
        if (i != j):  
            (min, avg, max, eq_count) =  _edit_distance(j, i, matrix)
            if (avg < min_avg):
                min_avg = avg;
                min_avg_index = i
            if (max < min_max):
                min_max = max;
                min_max_index = i
    
    return  (min_avg, min_avg_index,  min_max, min_max_index)

def do_distance(matrix, header):
    #           15   4   3   2  11   3   4   3   3
    #index_list=[16, 18, 15, 21, 28,  8,  6, 13, 11]
    # 15, 16, 3, 8, 13
    # 4, 18, 6
    avg_map=defaultdict(list)
    for i in range(1, len(matrix[1])-1):
        for j in range(1, len(matrix[1])-1):
            (c_min, c_avg, c_max, eq_count)  = _edit_distance(i, j, matrix)
            avg_map[c_avg].append((i, j, c_min, c_avg, c_max, eq_count))

    for key in sorted(avg_map.keys()):
        values = avg_map.get(key)
        for (i, j, c_min, c_avg, c_max, eq_count) in values:
            print(key, ":", i, j, "min:", c_min, "avg:",  c_avg, "max:", c_max, "eq_count:", eq_count, eq_count/float(len(matrix[1])))


if  __name__ == "__main__" :
    file_name = sys.argv[1]

    (header, matrix) = _get_matrix(file_name)
    do_distance(matrix, header)
    for key in [15,16,8,3,13]:
            print(key, header[key])
    print('')
    for key in [4,18]:
            print(key, header[key])
    print('')
    for key in [2,21]:
            print(key, header[key])

