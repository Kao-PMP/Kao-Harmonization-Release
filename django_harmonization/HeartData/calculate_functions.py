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
from datetime import datetime
from HeartData.concepts import YES_CONCEPT_ID
from HeartData.concepts import NO_CONCEPT_ID


logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# value triples:  (string, number, concept_id)


def sum(_, arg_list):
    sum=0
    for tuple in arg_list:
        (_, num, _) = tuple
        sum += num
    return sum 

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

# dates:(randomization date, death date)
def death_days(dates, values):
    if (len(dates) < 2):
        return None # not everybody dies
    elif (dates[0] == None or dates[1] == None):
        logger.error("calculate_functions().death_days() bad dates? %s", dates)
        return None
    else:
        rand_date = dates[0]  # will be same as string part of randomization_date_tuple
        death_date = dates[1]
        delta = death_date - rand_date
        #logger.debug("death_days() dates:%s values:%s  f_val:%s", dates, values,  delta)
        logger.info("death_days() dates:%s values:%s  f_val:%s", dates, values,  delta)
        if (delta.days < 0):
            logger.error("ERROR negative? %s", dates)
        return delta.days

def eos_to_death_days(dates, values):
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

def eos_days(dates, values):
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


def eos_death_max_days(dates, values):
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

def eos_death_min_days(dates, values):
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
                     height_in_tuple, weight_tuple, e);
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


def concept_or_list(dates, tuple_list):
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
