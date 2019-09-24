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
 calculate_functions.py
 Python Version: 3.6.3

 This is research code for demonstration purposes only.

 croeder 7/2017 chris.roeder@ucdenver.edu
'''
import sys
import re
import psycopg2
import psycopg2.extras
import logging
import string
import traceback
from datetime import datetime
from HeartData.concepts import YES_CONCEPT_ID
from HeartData.concepts import NO_CONCEPT_ID
from simpleeval import simple_eval

logger = logging.getLogger(__name__) # pylint: disable=locally-disabled, invalid-name
 
class InputError(Exception):
    """Exception raised for errors in the input.
    """
    def __init__(self, message):
        self.message = message


# value triples:  (string, number, concept_id)

# SIGNATURE 1 var-args style
############################################################
def run_simple_eval(dates, values, names, expression):
    """ param dates: a list of dates
        param values: a list of value triples, its a numerical expression so this will only work on the middle item of each triple: the number 
            The values take the form of triples allowing for an interfacw with different value types: string, number or concept.
            The numbers are cast as floats?
        param names: names corresponding to the values, referenced in the expression string
        
        min an max are supplied as predefined functions. This list may grow over time.
    """

    if len(values) != len(names):
        raise InputError("different number of  values and names in run_simple_eval")

    i=0;
    variables={}
    while i < len(values):   
        if values[i][1] is None:
            return None; # BAIL OUT!
        try:
            variables[names[i]] = float(values[i][1])
        except Exception as e:
            raise InputError("{} value could not be cast as float {}".format(i, values[i][1]))
        i = i + 1

    functions={
                "min": lambda x,y: min(x,y), 
                "max": lambda x,y: max(x,y)
    }

    try:
        value = simple_eval(expression, names=variables, functions=functions)
    except Exception as e:
        logger.error("simple_eval errored. expr:%s, functions:%s  names_map:%s ", expression, functions, names)
        #(exc_type, exc_value, exc_traceback) = sys.exc_info()
        #traceback.print_tb(exc_traceback, limit=4, file=sys.stdout)
        raise e

    return(value)

def sum(dates, arg_list, names, expression):
    sum=0
    for tuple in arg_list:
        (_, num, _) = tuple
        sum += num
    return sum 


def concept_or_list(dates, tuple_list, names, expression):
    """ Input: list of tuples of (string, number, concept_id) where the concepts are SNOMED for true or false.
        Process: extracts the concept_id value of the arguments, interprets them as the SNOMED concepts
        for truth and returns the SNOMED concept for the OR of the inputs.
        Output: single concept_id for true or false
    """
    value =  False
    for tuple in tuple_list:
        (_, _, concept) = tuple
        value = value or (concept == YES_CONCEPT_ID)

    if value:
        return YES_CONCEPT_ID
    else:
        return NO_CONCEPT_ID

def concept_and_list(dates, tuple_list, names, expression):
    """ Input: list of tuples of (string, number, concept_id) where the concepts are SNOMED for true or false.
        Process: extracts the concept_id value of the arguments, interprets them as the SNOMED concepts
        for truth and returns the SNOMED concept for the OR of the inputs.
        Output: single concept_id for true or false
    """
    value = True
    for tuple in tuple_list:
        (_, _, concept) = tuple
        value = value and (concept == YES_CONCEPT_ID)

    if value:
        return YES_CONCEPT_ID
    else:
        return NO_CONCEPT_ID


def corona_smoking_to_yesno(dates, tuple_list, names, expression):
    """   
        id, code, abbreviated name
        4144272, 266919005, never
        4310250, 8517006,   ex
        4144273, 266920004, trivial
        4298794, 77176002,  smoker
        not (concepts.py)  SMOKE_CURRENT_CONCEPT_ID=40766945    # LOINC 64234-8
    """   
    value =  False
    for tuple in tuple_list:
        (_, _, concept) = tuple
        value = value or (concept == 4298794)

    if value:
        return YES_CONCEPT_ID
    else:
        return NO_CONCEPT_ID

# dates:(randomization date, death date)
def death_days(dates, values, names, expression):
    if (len(dates) < 2):
        return None # not everybody dies
    elif (dates[0] == None or dates[1] == None):
        logger.error("calculate_functions().death_days() bad dates? %s", dates)
        return None
    else:
        rand_date = dates[0]  # will be same as string part of randomization_date_tuple
        death_date = dates[1]
        delta = death_date - rand_date
        logger.debug("death_days() dates:%s values:%s  f_val:%s", dates, values,  delta)
        if (delta.days < 0):
            logger.error("ERROR negative? %s", dates)
        return delta.days

def eos_to_death_days(dates, values, names, expression):
    if len(values) > 0:
        (_, eos_days, _) = values[0] 
        if len(values) > 1:
            death_status = values[1]
        else:
            death_status = None
        if death_status == None or death_status == NO_CONCEPT_ID:
           return eos_days
        else:
            return None
    else:
        logger.error("eos_to_death_days() no values at all %s %s", dates, values)
        return None

def eos_days(dates, values, names, expression):
    if len(values) > 1:
        # '2014-04-28 17:59:59'
        (eos_string, _,  _) = values[0]
        eos_date = datetime.strptime(eos_string.split(" ")[0], '%Y-%m-%d')

        # '2011-12-05'
        (rand_string, _,  _) = values[1]
        rand_date = datetime.strptime(rand_string.split(" ")[0], '%Y-%m-%d')

        if (eos_date == None or rand_date == None):
            return None
        else:
            delta = eos_date - rand_date
            logger.info("eos_days() dates:%s f_val:%s", dates, delta) # TODO
            return delta.days
    else:
        logger.error("eos_days() not enough values  %s %s", dates, values)
        return None


def eos_death_max_days(dates, values, names, expression):
    ''' EOS may be after death, return the earlier if both.
        var-args style to be able to deal with a None value when person has not died.
        arg0: eos_days_tuple,
        arg1: death_days_tuple
    '''
    if len(values) == 0:
        return None

    (_, eos_days, _) =  values[0]

    if len(values) > 1 and values[1] != None:
        (_, death_days, _) = values[1]
    else:
        death_days = sys.maxsize

    if eos_days != None :
        if (eos_days < death_days):
            eos_days = death_days
        return eos_days
    else:
        logger.error("eos_death_min_years() no values at all %s %s", dates, values)
        return None

def eos_death_min_days(dates, values, names, expression):
    ''' EOS may be after death, return the earlier if both.
        var-args style to be able to deal with a None value when person has not died.
        arg0: eos_days_tuple,
        arg1: death_days_tuple
    '''
    if len(values) == 0:
        logger.error("eos_death_min_years() no values at all-1 %s %s", dates, values)
        return None

    (_, eos_days, _) =  values[0]

    if len(values) > 1 and values[1] != None:
        (_, death_days, _) = values[1]
    else:
        death_days = sys.maxsize

    if eos_days != None :
        if (eos_days > death_days):
            eos_days = death_days
        return eos_days
    else:
        logger.error("eos_death_min_years() no values at all-2 %s %s", dates, values)
        return None


def _is_ascending(values): # TEST
    '''
        Tells if the values here go up or down. 
        Values can be either a single tuple, or a series of tuples with a None number value 
        at the beginning or end. Tuples have (string, int, concept_id) values. We only look at 
        the numbers/ints here.
        Ascending tarts with an ascending list of numbers. The last is None.
        Descending starts with a None, followed by a list of descending numbers.
        NB. The values list here has (should have) the inital value used in ranges_to_rank sliced off.
    '''
    logger.info("_is_ascending")
    # TODO throw on those asserts...figure out how to communicate that back to the UI
    ascending=values[0][1] is not None

    if ascending:
        # really just verifying the rest of the list corresonds to what the 
        # presence or absence  of an initial null says
        if len(values) == 1: 
            # self.assertTrue(values[][1] is not null)
            print('')
        elif len(values) == 2:
            if values[1][1] is not None:
                raise Exception("bogus list in _is_ascending, need at least one None")
        elif len(values) > 2: 
            for i in range(1, len(values) ):
                if values[i][1] is not None:  
                    if values[i][1] <= values[i-1][1]:
                        raise Exception("bogus list in _is_ascending, can't have descending values")
    else:
        if len(values) == 1: 
            # self.assertTrue(values[][1] is not null)
            print('')
        elif len(values) == 2:
            print("2", values)
            if values[1][1] is None:
                raise Exception("bogus list in _is_ascending, can't have two Nones")
        elif len(values) > 2: 
            for i in range(2, len(values) ):
                if values[i][1] > values[i-1][1]:
                    raise Exception("bogus list in _is_ascending, can't have ascending values")


    return ascending

def ranges_to_rank(dates, values, names, expression): # TEST
    """ TBD
        dates is unused
        values is an array that contains the value to be ranked followed by the numerical break points.
            Since they are values in this OMOP context, the are triples (string, number, concept_id) and
            we just use the number.
        names is an array that contains the rank values associated with the break points. There is one
            less of these than values. They are numerical, but called names.
        expression is unused
    """

    logger.info("values:%s, names:%s", values, names)
    if len(values) < 2:
        logger.error("too few values:%s.  dates:%s, names:%s, expression:%s ", values,  dates, names, expression)
        return None
 
    ascending = _is_ascending(values[1:])

    # validate that the ranks are numbers
    for i in range(1, len(names)-1 ):
        # TODO throw on those conditions...figure out how to communicate that back to the UI
        test_int = int(names[i])

    # validate that we have the same amount of values as names
    if len(values) != len(names):
        logger.error("num values:%s doesn't match names:%s", values,  names)
        raise Exception("bad input in ranges_to_rank")

    # CALCULATE 
    try:
        value = values[0]
        if value[1] is None:
            logger.warning("None input to r_to_r value:%s  [%s] [%s] \"%s\"", value[1], values, names, expression)
            return None
        for i in range(1, len(values) ):
            limit = values[i][1] # middle value of the ith tuple
    
            if (ascending):
                logger.info("ascending i:{} name:{} limit:{} value:{}".format(i, names[i], limit, value[1]))
            else:
                logger.info("descending i:{} name:{} limit:{} value:{}".format(i, names[i], limit, value[1]))
    
            if ascending:
                if limit == None or limit == 'null': # interpret as infinity, signal that it's the last rank in the list
                   return int(names[i])
                elif value[1] <= float(limit):
                   return int(names[i])
            else:
                if limit is None and len(values)==2:
                    return int(names[i])
                elif limit is None and value[1] > values[i+1][1]: 
                    return int(names[i])
                elif limit is not None and value[1] > float(limit):
                    return int(names[i-1])
                elif limit is not None and i == len(values) -1:
                    return int(names[i])
    except Exception as e:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=4, file=sys.stdout)
        raise e
        

    logger.error("returning None: dates:%s, values:%s, names:%s, expression:%s", dates, values, names, expression)
    return None

def map_concept_id(dates, values, names, expression):
    ''' 
        Looks for matches of the first item in the list of values with remaning items, 
        and returns the corresponding name. The concept_id part of the values is used, others ignored.
        (Recall that the values are triples: (string, number, concept_id))

        Ex: values =  [ (_, _, 456),   (_, _, 123), (_, _, 456), (_, _, 789)]
            names  = [ _, 'a', 'b', 'c' ]
        The first value, concept_id 456 matches the 2nd value in the list of remaining values.
        The second name is 'b', which is returned.

        param dates is unused
        param values: the first is the input concept, following are the 
            value-concepts that map to values in the names list
        param names  the list of return values. If the nth value is matched, the nth name is returned.
        param expression is unused.
    
        NB: the calling function acts differently when the table is "dual". Instead of reading the 
        value associated with (vocab_id, concept_code) in the named table (like observation), the 
        concept_code is return. It's mind bending and meta because often the concept_code is rather a concept_id.
        In this case you're matching concept IDs instead of values associated with concepts.
    ''' 

    logger.info("values:%s, names:%s", values, names)
    if len(values) < 1: 
        logger.error("map_concept_id() too few values! %s, %s, %s, %s", dates, values, names, expression)
        return None

    # find index of match
    i=1
    for value in values[1:]:
        logger.error("map_concept_id()  %s --> %d, %s             %s", values[0], i, values[i], values[1:] )
        if value[2] == values[0][2]:
            logger.error("map_concept_id() returning %s, %s     %s, %s, %s, %s", i, names[i], dates, values, names, expression)
            return names[i] 
        i=i+1

    logger.error("map_concept_id() bogus! %s, %s, %s, %s", dates, values, names, expression)
    return None

    


## SIGNATURE 2 explicitly listed tuples
########################################################################


def metric_bmi(dates, height_cm_tuple, weight_kg_tuple):
    """ caculates BMI from height in cm and weight in Kg
        https://www.cdc.gov/healthyweight/assessing/bmi/childrens_bmi/childrens_bmi_formula.html
        Note the division by 100 to convert from cm to m as called for by the formula in the above link.
        Recal value-triples: (string, number, concept_id), only the numbers are used here.
        param dates (unused)
        param height_cm_tuple: (_, height_cm, _)
        param weight_kg_tuple: (_, weight_kg, _)
    """
    try:
        weight = float(weight_kg_tuple[1]) 
        height_m = float(height_cm_tuple[1]) / 100.0
        retval= weight/float(height_m * height_m)
        return retval
    except Exception as e:
        logger.error("metric_bmi() threw errors with input '%s', '%s', exception:%s", 
                     height_cm_tuple, weight_kg_tuple, e)
    return None

def best_bmi(dates, height_in_tuple, weight_tuple):
    ## select n1.patientid,n1.Data_date,((N1.Data_string*703)/pow(n2.Data_string,2)),'(lb*703)/in^2','BMI'
    try:
        weight = float(weight_tuple[1]) 
        height_in = float(height_in_tuple[1]) 
        retval= weight*703/float(height_in * height_in)
        logger.debug("BMI %s, %s --> %s", height_in_tuple, weight_tuple, retval);
        return retval
    except Exception as e:
        logger.error("best_bmi() threw errors with input '%s', '%s', exception:%s", 
                     height_in_tuple, weight_tuple, e)
    return None

def best_creatinine_clearance(dates, age_tuple, race_tuple, sex_tuple, cre_tuple):
    try:
        age = float(age_tuple[1]) 
        cre = float(cre_tuple[1]) 
        retval=-99

        if (race_tuple[2] == '15086000'): # TODO correct for African American?
            if (sex_tuple[2] == '703111700'): # TODO make constants at top of file...
                #race=AA, sex=male
                retval= 141*pow(min(cre/0.9,1), -0.411) * pow(max(cre/0.9,1), -1.209) * pow(0.993, age) * 1.159
            else:
                #race=AA, sex=female
                retval= 141*pow(min(cre/0.7,1), -0.329) * pow(max(cre/0.7,1), -1.209) * pow(0.993, age) * 1.1018 * 1.159
        else:
            if (sex_tuple[2] == '703111700'):
                #race!=AA, sex=male
                retval= 141*pow(min(cre/0.9,1), -0.411) * pow(max(cre/0.9,1), -1.209) * pow(0.993, age) 
            else:
                #race!=AA, sex=female
                retval = 141*pow(min(cre/0.7,1), -0.329) * pow(max(cre/0.7,1), -1.209) * pow(0.993, age) * 1.081

        logger.debug("CrCl: %s, %s, %s, %s --> %s", age_tuple, race_tuple, sex_tuple, cre_tuple, retval)
        return retval
    except Exception as e:
        logger.error("best_creatinine_clearance() threw errors with input %s, %s, %s, %s exception:%s", 
                     age_tuple, race_tuple, sex_tuple, cre_tuple, e);

    return None


def best_logical_concept_or(dates, a_tuple, b_tuple):
    """ extracts the concept_id value of the arguments, interprets them as the SNOMED concepts
        for truth and returns the SNOMED concept for the OR of the inputs.
    """
    (_, _, a_concept) = a_tuple
    (_, _, b_concept) = b_tuple
    
    retval =  NO_CONCEPT_ID


    # if (a_concept == YES_CONCEPT_ID or b_concept == YES_CONCEPT_ID):

    if (a_concept == YES_CONCEPT_ID):
        retval = YES_CONCEPT_ID

    if (b_concept == YES_CONCEPT_ID):
        retval = YES_CONCEPT_ID

    if (a_concept == YES_CONCEPT_ID or b_concept == YES_CONCEPT_ID):
        logger.info("best_logical_concept_or %s %s  %s", a_tuple, b_tuple, retval)

    logger.debug("best_logical_concept_or()  (valvular disease or BBB): %s, %s --> %s", 
            a_tuple, b_tuple, retval)

    return retval

#heart_2017-12-06=# insert into ohdsi_calculation_argument values ('UCD.Kao', 'UCD-Kao-23', 4, 'topcat_death', 1, 'Site Death days', 'value_as_number', 'UCD-Kao-18', 'UCD.Kao', 'observation');
#heart_2017-12-06=# insert into ohdsi_calculation_argument values ('UCD.Kao', 'UCD-Kao-24', 4, 'topcat_death', 2, 'CEC Death days', 'value_as_number', 'UCD-Kao-18', 'UCD.Kao', 'observation');
#heart_2017-12-06=# insert into ohdsi_calculation_argument values ('UCD.Kao', 'UCD-Kao-25', 4, 'topcat_death', 3, 'Site vs CEC Death type', 'value_as_number', 'UCD-Kao-18', 'UCD.Kao', 'observation');

def topcat_death(dates, site_death_days, cec_death_days, site_vs_cec):
    if site_vs_cec == 1:
        return site_death_days
    elif site_vs_cec == 2:
        return cec_death_days
    else:
        return None

def if_null(dates, a, b) :
    ''' if a is not null, then a, else b '''
    if a != None:
        return a
    else:
        return b

def concept_identity(dates, tuple):
    (_, _, concept) = tuple;
    return concept;    

def average_minus_one(_, arg_list):
    sum=0
    n=0
    for num in arg_list:
        sum += (num -1)
        n += 1
    return sum / float(n)

## Calculate pulse pressure (bpsys-bpdias)
def best_pulse_pressure(_, bpsys_tuple, bpdias_tuple):
    retval =  bpsys_tuple[1] - bpdias_tuple[1];
    logger.debug("Pulse Pressure: %s, %s --> %s", bpsys_tuple, bpdias_tuple, retval)
    return retval

def subtract(_, a_tuple, b_tuple):
    return difference(_, a_tuple, b_tuple)
 
def difference(_, a_tuple, b_tuple):
    if a_tuple[1] is None or b_tuple[1] is None:
        return None
    retval =  a_tuple[1] - b_tuple[1];
    return retval


def true(_):
    return 4188539
