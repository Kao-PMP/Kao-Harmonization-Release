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
 dependent_columns.py
 Python Version: 3.6.3
    
 Find a column that is very similar to others from the extracted analysis matrix. Concretely, this
 script finds the stand-alone probability of a value in a columna and compares it with the conditional
 probability of another column having a different (it's most popular) value. 

 usage: dependent_columns.py <matrix file>
 output: the really badly dependent columns

    "a,   b,   value, p(a=value), p(a=value|b=value)
    CAD   CABG 2.0 0.640333333333 0.981661272923

 NB. a healthy value for one phenotype often comes with healthy values for other phenotypes, so
 I discount signs of dependence on values associated with a healthy state. 

 This is research code for demonstration purposes only.

 croeder 10/2017 chris.roeder@ucdenver.edu
 independant ==> p(a) = p(a|b) 
'''


import sys
import csv
import re
from collections import defaultdict
import types 

RATIO_CUTOFF_L = 0.5
RATIO_CUTOFF_H = 2.0
MAX_VALUES=5


CONTINUOUS_NAMES = {'Weig', 'KCCQ', 'CrCv', 'Tota', 'SBPv', 'HR v', 'LVFv', 'BNP'}

def _get_matrix(file_name):
    """ Reads the analysis matrix to analyze. Trims header row and id column (1st of each) """
    # return reader[1:][1:]

    header = None
    with  open(file_name, "r") as file:
        matrix = []
        reader = csv.reader(file)
        for string_row in reader:
            number_row=[]
            if header == None:
                header = string_row
            else:
                for s in string_row:
                    s = s.strip()
                    if s == "NA":
                        number_row.append(None) 
                    elif type(s) == types.StringType and s[0] == '\'' and s[-1] == '\'':
                        clean_string = re.search('\'(.+)\'', s).group(1)
                        number_row.append(clean_string) # use re to remove quotes
                    else:
                        number_row.append(float(s)) 

            matrix.append(number_row)
        # add in a test case that is identical ...
        return (header, matrix)


def _get_value_counts(index_a, index_b, matrix):
    """ Returns three dictionaries. The first two represent frequency distributions of columns indexed by a and b. 
        The third counts how often a value appears in both columns 
        (value -> frequency in a, value -> frequency in b, value -> frequency in both)
    """
    col_a = defaultdict(int)
    col_b = defaultdict(int)
    both = defaultdict(int)
    for row in matrix:
        if index_a < len(row) and  index_b < len(row):
            val_a = row[index_a]
            col_a[val_a] += 1

            val_b = row[index_b]
            col_b[val_b] += 1

            if row[index_a] == row[index_b] and row[index_a] != None:
                both[row[index_a]] += 1

    return (col_a, col_b, both)


def _probability(value, col_a_counts_map):
    """ p(a=value) = counts of a at value, dividied by total values of a """    
    sum=0
    for key in col_a_counts_map.keys():
        sum += col_a_counts_map[key]

    if  col_a_counts_map[value] == 0:
        print("nothing:", value)
    return col_a_counts_map[value] / float(sum)

def _conditional_probability(col_a_counts_map, col_b_counts_map, both_counts_map):
    """ For values that a might take, maps to  p(a=v|b=v).
        = the number  f times both columns a and b have a value divided by the number of times column b has that value.
        returns: value->prob for given maps.
        NB: note that it insists on the value being the same on both sides.
    """
    map={}
    for key in col_a_counts_map.keys(): # a here because it's only values of a we care about
        if (key in col_b_counts_map.keys()):
            conditional_prob = both_counts_map[key] / float(col_b_counts_map[key]) # b here because it's the prior
            map[key]=conditional_prob

    return map


# ----------------------------------------------------------------------------------------------



def _find_all_pairs(list):
    """ returns all pairs created from the given list. (a, b) is not the same as (b, a). """

    pairs = set(); 
    for value_a in list:
        for value_b in list:
            pairs.add((value_a, value_b)) 

    return pairs


def _frequency_of_pair(a, b, v, w, matrix):
    """ builds a map from (v, w) -> (p(a=v and b=w) for all possible pairs (v, w) 
        a, b indeces of columns to be compared
        v, w respective values of columns a and b, we're looking at
        (not cheap)
    """
    count=0
    worry_count=0
    for row in matrix:
        if a < len(row) and  b < len(row):
            if row[a] == v and row[b] == w:
                count += 1 
        else :  
            ##print "worry?", a, b, len(row), row
            worry_count += 1

    return count


def _relatedness_of_pairs(a, b, col_a_counts_map, col_b_counts_map, both_counts_map, matrix):
    """ For all pairs of values (v, w) shared between columns (keys in both_counts_map), maps (v, w) to  p(a=v|b=w).
        returns: (v, w) -> p(a=v) / p(a=v | b=w)  as a measure of relatedness.
            A ratio of 1.0 means they are independent. The more the ratio drops below 1, the more the condition of b
            affects a.
    """
  
    map={}
    if len(both_counts_map.keys()) < MAX_VALUES :
        value_pairs_list = _find_all_pairs(both_counts_map.keys())
        for value_pair in value_pairs_list:
             # p(a=v | b=w) =  p(a=v ^ b=w) / p(b=w)
             #              =  (count(a and b) / rows-in- matrix)  /  (count(b=w)  / rows-in-matrix)
             #              =  counts(a and b)  / count(b=w)
             cond_prob = _frequency_of_pair(a, b, value_pair[0], value_pair[1], matrix) / float(col_b_counts_map[value_pair[1]]) 
             if  cond_prob != 0:
                 prob = _probability(value_pair[0], col_a_counts_map)
                 map[value_pair] = cond_prob / float(prob)

    return map


def _all_pairs_all_values(header, matrix):
    """For all pairs of columns/phenotypes, and for all values shared in each pair, find the relatedness between columns for each   """

    uber_map={}
    for i in range (1, len(header)):
        if header[i].strip() not in CONTINUOUS_NAMES:
            for j in range (1, len(header)):
                if header[j].strip() not in CONTINUOUS_NAMES and i !=j:
                    (col_a_counts_map, col_b_counts_map, both_counts_map) = _get_value_counts(i,j , matrix)    
                    map = _relatedness_of_pairs(i, j, col_a_counts_map, col_b_counts_map, both_counts_map, matrix)
                    uber_map[(i,j)]=map

    return uber_map

def show_uber_map(header, matrix):
    uber_map = _all_pairs_all_values(header, matrix)
    for (pair, map) in uber_map.items():
        show=False
        sum=0
        n=0
        if len(map) > 0:
            for (value, ratio) in map.items():
                sum += ratio
                n += 1
                if (ratio < RATIO_CUTOFF_L or ratio > RATIO_CUTOFF_H) and pair[0] != pair[1]:
                    show=True
            average = sum / float(n)
            if show or average < RATIO_CUTOFF_L or average > RATIO_CUTOFF_H:
                print(pair, header[pair[0]], header[pair[1]])
                for (value, ratio) in map.items():
                    if (ratio < RATIO_CUTOFF_L or ratio > RATIO_CUTOFF_H) :
                        print("    [value:{} ratio:{}] ".format( value, ratio))
                print("")
 

if  __name__ == "__main__" :
    file_name = sys.argv[1]

    (header, matrix) = _get_matrix(file_name)

    show_uber_map(header, matrix)   

