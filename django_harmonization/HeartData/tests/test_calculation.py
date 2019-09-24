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
# from: .../<git>/django_harmonization/django_harmonization
# Handy: python3 -m unittest   HeartData.tests.test_calculation.CalculationTest.test_ranges_to_rank_desc
# Also:  python3 unittest discover

 
from django.test import TestCase
import HeartData.calculate_functions 
from HeartData.calculate_functions import _is_ascending
from HeartData.calculate_functions import concept_or_list
from HeartData.calculate_functions import concept_and_list
from HeartData.calculate_functions import _is_ascending
from HeartData.calculate_functions import sum
from HeartData.calculate_functions import true
from HeartData.calculate_functions import if_null
from HeartData.calculate_functions import difference
from HeartData.calculate_functions import run_simple_eval
from HeartData.calculate_functions import InputError
from HeartData.concepts import YES_CONCEPT_ID
from HeartData.concepts import NO_CONCEPT_ID

class CalculationTest(TestCase):
    #def setUp(self):
    #    print("test_calculation.setup()")

    # from a->x, b->y, c->z
    def test(self):
        """ begrudingly requires a connection to a database that has the metadata in it
        """
        print("CalculationTest.test()...")
        self.assertEqual(1,1)

        ##calc = new CalculatedFieldFunction(con, 1, "best_bmi")
        ##calc.test()
        

    def test_is_ascending(self):
        self.assertTrue(_is_ascending([ ('', 5, None), ('', 10, None), ('', None, None)]))
        self.assertTrue(_is_ascending([ ('', 5, None), ('', None, None)]))
        self.assertTrue(_is_ascending([('', 5, None)]))


        self.assertFalse(_is_ascending([ ('', None, None), ('', 10, None), ('', 5, None)]))
        self.assertFalse(_is_ascending([ ('', None, None), ('', 5, None)]))


        # throws/raises because it's wrong
        #_is_ascending([('', None, None)])
        #_is_ascending([ ('', None, None), ('', 5, None), ('', 10, None)])

    def test_map_concept_id(self):
        ''' the function gets the values here. It just looks to match the first value in the list of values starting with the second. '''

        # value triples:  (string, number, concept_id)
        names  = ['var_name', 'A', 'B', 'C']
        values = [ (None, None, 0), (None, None, 1), (None, None, 2), (None, None, 3)]
        retval = HeartData.calculate_functions.map_concept_id(None, values, names, None)
        self.assertEqual(retval, None)

        values = [ (None, None, 1), (None, None, 1), (None, None, 2), (None, None, 3)]
        retval = HeartData.calculate_functions.map_concept_id(None, values, names, None)
        self.assertEqual(retval, 'A')

        values = [ (None, None, 2), (None, None, 1), (None, None, 2), (None, None, 3)]
        retval = HeartData.calculate_functions.map_concept_id(None, values, names, None)
        self.assertEqual(retval, 'B')

        values = [ (None, None, 3), (None, None, 1), (None, None, 2), (None, None, 3)]
        retval = HeartData.calculate_functions.map_concept_id(None, values, names, None)
        self.assertEqual(retval, 'C')

        values = [ (None, None, 4), (None, None, 1), (None, None, 2), (None, None, 3)]
        retval = HeartData.calculate_functions.map_concept_id(None, values, names, None)
        self.assertEqual(retval, None)


    def test_ranges_to_rank_asc(self):
        print("test_calculation.test_ranges_to_rank_asc")
        # 3
        self._test_ranges_to_rank_asc(
            [1, 5, 6, 10, 11],
            [('', 5, None), ('', 10, None), ('', None, None)],
            ['value', '1', '2', '3'],
            [1, 1, 2, 2, 3])

        # 3
        self._test_ranges_to_rank_asc(
            [None, None, 6, 10, 11],
            [('', 5, None), ('', 10, None), ('', None, None)],
            ['value', '1', '2', '3'],
            [None, None, 2, 2, 3])
    
        #print("-------------")

        self._test_ranges_to_rank_asc(
            [11, 10, 1, 5, 6],
            [('', 5, None), ('', 10, None), ('', None, None)],
            ['value', '1', '2', '3'],
            [3, 2, 1, 1, 2 ])

        #print("-------------")

        #2
        self._test_ranges_to_rank_asc(
            [1, 5, 6, 10, 11],
            [('', 5, None), ('', None, None)],
            ['value', '1', '2'],
            [1, 1, 2, 2, 2])

        #2
        self._test_ranges_to_rank_asc(
            [1, None, 6, 10, 11],
            [('', 5, None), ('', None, None)],
            ['value', '1', '2'],
            [1, None, 2, 2, 2])

        #3
        self._test_ranges_to_rank_asc(
            [1, 5, 6, None, 11],
            [('', 5, None), ('', None, None)],
            ['value', '1', '2'],
            [1, 1, 2, None, 2])

        #print("-------------")

        #1  direction doesn't mean anything when just one, this works out as a descending
        # ....uncommented copy is down with the other desc tests
        #self._test_ranges_to_rank_desc(
        #    [1, 5, 6, 10, 11],
        #    [('', None, None)],
        #    ['value', '1'],
        #    [1, 1, 1, 1, 1])

        #print("-------------")

        # 1 wrong
#        self._test_ranges_to_rank_asc(
#            [1, 5, 6, 10, 11],
#            [('', 1, None)],
#            [1, 1, 2, 2, 2])

        # different numbers of argumetns:.....

        # ranks must be numbers....

    def _test_ranges_to_rank_asc(self, test_values_asc, ranges_ascending_starter, names, correct_ranks_asc ):
        # Values are less or equal to the break value. 
        # (string, number, concept_id) only number field is used here 

        dates = [] 
        expression = '' 
        i=0
        self.assertTrue(_is_ascending( ranges_ascending_starter  ))
        for val in test_values_asc:
            tuple = ('', val, None)
            ranges_ascending = ranges_ascending_starter.copy()
            ranges_ascending.insert(0, tuple)
            rank = HeartData.calculate_functions.ranges_to_rank(dates, ranges_ascending, names, expression)
            self.assertEqual(rank, correct_ranks_asc[i])
            #print("PASS")
            i=i+1


    def _test_ranges_to_rank_desc(self):
        print("test_calculation.test_ranges_to_rank_desc")

        self._test_ranges_to_rank_desc(
            [11, 10, 6, 5, 1],
            [('', None, None), ('', 10, None), ('', 5, None)],
            ['value', '1', '2', '3'] ,
            [1, 2, 2, 3, 3 ])

        #print("-------------")

        self._test_ranges_to_rank_desc(
            [1, 6, 5,  11, 10],
            [('', None, None), ('', 10, None), ('', 5, None)],
            ['value', '1', '2', '3'] ,
            [3, 2, 3, 1, 2 ])

        self._test_ranges_to_rank_desc(
            [1, 6, None,  11, 10],
            [('', None, None), ('', 10, None), ('', 5, None)],
            ['value', '1', '2', '3'] ,
            [3, 2, None, 1, 2 ])

        #print("-------------")

        self._test_ranges_to_rank_desc(
            [11, 10, 6, 5, 1],
            [('', None, None), ('', 5, None)],
            ['value', '1', '2'] ,
            [1, 1, 1, 2, 2])

        #print("-------------")

        self._test_ranges_to_rank_desc(
            [5, 11, 10, 6, 5, 1],
            [('', None, None), ('', 5, None)],
            ['value', '1', '2'] ,
            [2, 1, 1, 1, 2, 2 ])

        #print("-------------")

        self._test_ranges_to_rank_desc(
            [1, 5, 6, 10, 11],
            [('', None, None)],
            ['value', '1'],
            [1, 1, 1, 1, 1])

        self._test_ranges_to_rank_desc(
            [1, 5, 6, None, 11],
            [('', None, None)],
            ['value', '1'],
            [1, 1, 1, None, 1])

    def _test_ranges_to_rank_desc(self, test_values_desc, ranges_descending_starter, names, correct_ranks_desc):
        # Values are greater than the break value. 
        dates = [] 
        expression = '' 
        i=0
        self.assertFalse(_is_ascending( ranges_descending_starter  ))
        for val in test_values_desc:
            tuple = ('', val, None)
            ranges_descending = ranges_descending_starter.copy()
            ranges_descending.insert(0, tuple)
            rank = HeartData.calculate_functions.ranges_to_rank(dates, ranges_descending, names, expression)
            self.assertEqual(rank, correct_ranks_desc[i]) 
            #print("PASS")
            i=i+1

    # def sum(dates, arg_list, names, expression):
    def test_sum_1(self):
        args = [ ]
        self.assertEqual(sum(None, args, None, None), 0)

    #def test_sum_2(self):
    #    args = [(None, None, None) ]
    #    self.assertEqual(sum(None, args, None, None), 0)

    #def test_sum_3_1(self):
    #    args = [(None, 1, None), (None, None, None) ]
    #    self.assertEqual(sum(None, args, None, None), 1)

    def test_sum_3(self):
        args = [(None, 1, None) ]
        self.assertEqual(sum(None, args, None, None), 1)

    def test_sum_4(self):
        args = [(None, 1, None), (None, 2, None) ]
        self.assertEqual(sum(None, args, None, None), 3)


    def test_concept_or_list_1(self):
        args = [ (None, None, None) ] 
        self.assertEqual(concept_or_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_or_list_2(self):
        args = [ (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_or_list(None, args, None, None), YES_CONCEPT_ID)

    def test_concept_or_list_3(self):
        args = [ (None, None, NO_CONCEPT_ID) ] 
        self.assertEqual(concept_or_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_or_list_4(self):
        args = [ (None, None, NO_CONCEPT_ID), (None, None, NO_CONCEPT_ID) ] 
        self.assertEqual(concept_or_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_or_list_5(self):
        args = [ (None, None, NO_CONCEPT_ID), (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_or_list(None, args, None, None), YES_CONCEPT_ID)

    def test_concept_or_list_6(self):
        args = [ (None, None, YES_CONCEPT_ID), (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_or_list(None, args, None, None), YES_CONCEPT_ID)

    def test_concept_or_list_7(self):
        args = [ (None, None, YES_CONCEPT_ID), (None, None, NO_CONCEPT_ID) ] 
        self.assertEqual(concept_or_list(None, args, None, None), YES_CONCEPT_ID)

    def test_concept_and_list_1(self):
        args = [ (None, None, None) ] 
        self.assertEqual(concept_and_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_and_list_2(self):
        args = [ (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), YES_CONCEPT_ID)

    def test_concept_and_list_3(self):
        args = [ (None, None, NO_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_and_list_4(self):
        args = [ (None, None, NO_CONCEPT_ID), (None, None, NO_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_and_list_5(self):
        args = [ (None, None, NO_CONCEPT_ID), (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_and_list_6(self):
        args = [ (None, None, YES_CONCEPT_ID), (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), YES_CONCEPT_ID)

    def test_concept_and_list_7(self):
        args = [ (None, None, YES_CONCEPT_ID), (None, None, NO_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_and_list_8(self):
        args = [ (None, None, YES_CONCEPT_ID), (None, None, YES_CONCEPT_ID), (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), YES_CONCEPT_ID)

    def test_concept_and_list_9(self):
        args = [ (None, None, NO_CONCEPT_ID), (None, None, YES_CONCEPT_ID), (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_and_list_10(self):
        args = [ (None, None, YES_CONCEPT_ID), (None, None, NO_CONCEPT_ID), (None, None, YES_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), NO_CONCEPT_ID)

    def test_concept_and_list_11(self):
        args = [ (None, None, YES_CONCEPT_ID), (None, None, YES_CONCEPT_ID), (None, None, NO_CONCEPT_ID) ] 
        self.assertEqual(concept_and_list(None, args, None, None), NO_CONCEPT_ID)

    def test_if_null_1(self)    :
        self.assertEqual(if_null(None, 'a', 'b'), 'a')

    def test_if_null_4(self)    :
        self.assertEqual(if_null(None, 'a', None), 'a')

    def test_if_null_2(self)    :
        self.assertEqual(if_null(None, None, 'b'), 'b')

    def test_if_null_3(self)    :
        self.assertEqual(if_null(None, None, None), None)


    def test_difference_1(self):
        self.assertEqual(difference(None, (None, 1, None), (None, 1, None)), 0)
    
    def test_difference_2(self):
        self.assertEqual(difference(None, (None, 1, None), (None, 2, None)), -1)
    
    def test_difference_3(self):
        self.assertEqual(difference(None, (None, 2, None), (None, 1, None)), 1)
   
    def test_difference_4(self):
        self.assertEqual(difference(None, (None, None, None), (None, None, None)), None)
   
    def test_difference_5(self):
        self.assertEqual(difference(None, (None, 1, None), (None, None, None)), None)
   
    def test_difference_6(self):
        self.assertEqual(difference(None, (None, None, None), (None, 1, None)), None)
   

    def test_simple_eval_0(self):
        # FYI: in my mind at least, it's easy to call simple_eval instead of run_simple_eval.
        # value triples:  (string, number, concept_id)
        values= [ ['foo', 2, 3579],  ['bar', 5, 122346], ['baz', 8, 9876] ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertEqual(run_simple_eval(None, values, names, expression), 15)

    def test_simple_eval_0a(self):
        values= [ ['foo', 2, 3579],  ['bar', 5, 122346], ['baz', 8, 9876] ]
        names=['a', 'b']
        expression='a+b+c'
        with self.assertRaisesMessage(InputError, 'different number of  values and names in run_simple_eval'):
            run_simple_eval(None, values, names, expression)

    def test_simple_eval_1_i(self):
        values= [ ('foo', 2, 3579),  ('bar', 5, 122346), ('baz', 8, 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertEqual(run_simple_eval(None, values, names, expression), 15)

    def test_simple_eval_1_f(self):
        values= [ ('foo', 2.1, 3579),  ('bar', 5.2, 122346), ('baz', 8.3, 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertTrue(abs(run_simple_eval(None, values, names, expression) -  15.6) < 0.000001)

    def test_simple_eval_1_fi(self):
        values= [ ('foo', 2, 3579),  ('bar', 5.2, 122346), ('baz', 8.3, 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertTrue(abs(run_simple_eval(None, values, names, expression) -  15.5) < 0.000001)

    def test_simple_eval_1_string(self):
        values= [ ('foo', 'x', 3579),  ('bar', 5.2, 122346), ('baz', 8.3, 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        with self.assertRaisesMessage(InputError, '0 value could not be cast as float x'):
            run_simple_eval(None, values, names, expression)

    def test_simple_eval_1_string_legit(self):
        values= [ ('foo', '2', 3579),  ('bar', '5.2', 122346), ('baz', '8.3', 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertTrue(abs(run_simple_eval(None, values, names, expression) -  15.5) < 0.000001)


    def test_simple_eval_2(self):
        values= [ ('foo', None, 3579),  ('bar', None, 122346), ('baz', None, 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertEqual(run_simple_eval(None, values, names, expression), None)

    def test_simple_eval_3(self):
        values= [ ('foo', 2, 3579),  ('bar', 5, 122346), ('baz', None, 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertEqual(run_simple_eval(None, values, names, expression), None)

    def test_simple_eval_4(self):
        values= [ ('foo', 2, 3579),  ('bar', None, 122346), ('baz', 8, 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertEqual(run_simple_eval(None, values, names, expression), None)

    def test_simple_eval_5(self):
        values= [ ('foo', None, 3579),  ('bar', None, 122346), ('baz', 8, 9876) ]
        names=['a', 'b', 'c']
        expression='a+b+c'
        self.assertEqual(run_simple_eval(None, values, names, expression), None)


    def test_true(self):
        self.assertEqual(true({}), 4188539)
        

#def run_simple_eval(dates, values, names, expression):
#    """ dates: a list of dates
#        values: a list of value lists that were collected on corresponding dates.
#            The values take the form of triples allowing for an interface with different value types: string, number or concept.
#            The configuration should work such that a function will only look at one of the types. The others can be null.
#        names: names corresponding to the values
#    """
#
#    if len(dates) != len(values) or len(values) != len(names):
#        raise InputError("different number of dates, values and names in run_simple_eval")
#
#    i=0;
#    variables={}
#    while i < len(values):   
#        variables[names[i]] = float(values[i][1])
#        i = i + 1
#
#    functions={
#                "min": lambda x,y: min(x,y), 
#                "max": lambda x,y: max(x,y)
#    }
#    try:
#        value = simple_eval(expression, names=variables, functions=functions)
#    except Exception as e:
#        logger.error("simple_eval errored. expr:%s, functions:%s   ", expression, functions)
#        (exc_type, exc_value, exc_traceback) = sys.exc_info()
#        traceback.print_tb(exc_traceback, limit=4, file=sys.stdout)
#        raise e
#
#    return(value)

#def concept_or_list(dates, tuple_list, names, expression):
#    """ Input: list of tuples of (string, number, concept_id) where the concepts are SNOMED for true or false.
#        Process: extracts the concept_id value of the arguments, interprets them as the SNOMED concepts
#        for truth and returns the SNOMED concept for the OR of the inputs.
#        Output: single concept_id for true or false
#    """
#    value =  False
#    for tuple in tuple_list:
#        (_, _, concept) = tuple
#
#
#
#
