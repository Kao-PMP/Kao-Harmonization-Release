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
 migrate_functions.py
 Python Version: 3.6.3
 
 This is research code for demonstration purposes only.


    These functions...

    Q: How to denote that each function has a common signautre ???
    Q: is it bad to include the return type of the function in the function name conflating functiong with return type?
       I think I saw this in the identity fucntion where you need to have for each of the types of values

 croeder 7/2017 chris.roeder@ucdenver.edu
 croeder 9/2018 gutted, parameterized
 croeder 4/2019 resurrected, stuff in person.py not parameterized yet
'''

import sys
import re
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import logging
import string
import traceback


logger = logging.getLogger(__name__)

def _lookup_concept_id(vocab_id, concept_code, con):
    stmt = """  SELECT concept_id
                FROM  concept c  
                WHERE c.vocabulary_id = %s and c.concept_code = %s 
            """
    with con.cursor() as cur:
        try:
            cur.execute(stmt, (vocab_id, concept_code))
            rows = cur.fetchall()
            if len(rows) > 0:
                return(rows[0][0])
        except Exception as e:
            print("Error in _lookup_concept_id", vocab_id, concept_code, e)
        else:
           return None
 
#############################################################################################
from HeartData.concepts import AFRICAN_AMERICAN_CONCEPT_ID 
from HeartData.concepts import CAUCASIAN_CONCEPT_ID
from HeartData.concepts import ASIAN_CONCEPT_ID
from HeartData.concepts import PACIFIC_ISLANDER_CONCEPT_ID
from HeartData.concepts import AMERICAN_INDIAN_CONCEPT_ID
from HeartData.concepts import HISPANIC_CONCEPT_ID
from HeartData.concepts import OTHER_RACE_CONCEPT_ID
from HeartData.concepts import MALE_CONCEPT_ID
from HeartData.concepts import FEMALE_CONCEPT_ID 
from HeartData.concepts import YES_CONCEPT_ID
from HeartData.concepts import NO_CONCEPT_ID

from HeartData.concepts import YES_CONCEPT_CODE
from HeartData.concepts import YES_VOCABULARY_ID
from HeartData.concepts import NO_CONCEPT_CODE
from HeartData.concepts import NO_VOCABULARY_ID
 
from HeartData.concepts import SMOKE_NEVER_CONCEPT_ID
from HeartData.concepts import SMOKE_CURRENT_CONCEPT_ID
from HeartData.concepts import SMOKE_SMOKELESS_CONCEPT_ID
from HeartData.concepts import SMOKE_FORMER_CONCEPT_ID
from HeartData.concepts import BARI2D_RACE_1_CONCEPT_ID
from HeartData.concepts import BARI2D_RACE_2_CONCEPT_ID

# ---- BEST -----
BEST_MALE=1
BEST_FEMALE = 2

BEST_YES=1
BEST_NO=2
 
 
# ---- HF-ACTION ---
HF_MEN=1
HF_WOMEN=2
# from the Data_Dictionary.pdf "1=Black, 2=White, 3=Asian, Amer Ind, Pac. Isl"
HF_AFRICAN_AMERICAN=1
HF_CAUCASIAN=2
HF_ASIAN=3 
HF_AMERICAN_INDIAN=4
HF_PACIFIC_ISLANDER=5
 
HF_YES=1
HF_NO=0
HF_YES_12=1
HF_NO_12=2
 
# -- SCD-HeFT --
SH_YES=1
SH_NO=0
 
SH_MALE=1
SH_FEMALE=2
 
SH_AFRICAN_AMERICAN="African American"
SH_CAUCASIAN ="Caucasian"
SH_ASIAN="Asian"
SH_LATIN_AMERICAN ="Latin American"
SH_OTHER="Other"
 
# -- TOPCAT --
TC_YES=1
TC_NO=0
 
TC_MALE=1
TC_FEMALE=2
 
TC_CAUCASIAN =1
TC_AFRICAN_AMERICAN=2
TC_ASIAN=3
TC_OTHER=4
 
# -- PARADIGM --
P_YES=1
P_NO=0
 
P_MALE=1
P_FEMALE=2
 
P_CAUCASIAN =1
P_AFRICAN_AMERICAN=2
P_ASIAN=3
P_OTHER=4
 
## TBD: ATMOSPHERE TODO
A_CAUCASIAN =1
A_AFRICAN_AMERICAN=2
A_ASIAN=3
A_NATIVE_AMERICAN=7
A_PAC_ISLAND=8
A_OTHER=88
 
AIMHIGH_OTHER_RACE=8
AIMHIGH_WHITE_RACE=5
AIMHIGH_BLACK_RACE=3
AIMHIGH_ASIAN_RACE=2
AIMHIGH_AM_INDIAN_RACE=1
 
AIMHIGH_SMOKE_NEVER=1
AIMHIGH_SMOKE_CURRENT=2
AIMHIGH_SMOKELESS=3
AIMHIGH_SMOKE_FORMER=4


###########
# functions in this first batch are not used in migrate, rather by person.py.
# They are deprecated and need to be worked out of usage in person.py
###########

 
############################################################################################
"""
    New function signature
        param value - a single value of either number, string, or concept_id (??) type
        param mapping - a StudyToOhdsiMapping object
        param arguments - a StudyMappingArguments object
        param con
"""

def true(_string_value, _mapping, _arguments, con):
    """ 
        Param string_value, unused
        Param mapping, unused
        Param arguments, unused
        Param con, unused
        returns concept_id of True
    """ 

    return  YES_CONCEPT_ID


def identity(value, _mapping, _arguments, con):
    """
        Param string_value, returned
        Param mapping, unused
        Param arguments, unused
        Param con, unused
        returns value
    """ 

    return value

    
def map_string(value, mapping, arguments, con):
    """ Converts a string value to a concept using rows from study_mapping_arguments.
            See also map_number() and map_concept() below.
        Param string_value
        Param mapping, the driving row from study_to_ohdsi_mapping describing the destination concept location in OMOP
        Param arguments, rows (in dict form)  from study_mapping_arguments that match strings to concepts
        Param con, a psycopg2 database connnection
          rows: (string_value, number_value, concept_value, map_target, factor, shift)
        returns concept_id of  vocabulary_id, concept_code of mapped value
    """ 

    concept_pair = None
    logger.info("migrate_functions.map_string value:%s mapping:%s", value, mapping)
    if (arguments and len(arguments) > 0):
        if value is None:
            return None

        for arg in arguments:
            if value == arg['mapped_string']:
                concept_pair =  (arg['to_concept_vocabulary_id'], arg['to_concept_code'])
            print(" string -->   ", value, arg['mapped_string'])
        if (not concept_pair):
            logger.error("migrate_functions.map_string() I think your arguments list for a mapping isn't complete. Not able to map this value: \"%s\"  arg:\"%s\" mapping:%s", 
                value, arguments, mapping)
            return None
        else:
            try:
                return _lookup_concept_id(concept_pair[0], concept_pair[1], con)
            except Exception as e:
                logger.error("Concept matching query does not exist \"%s\" \"%s\" value:%s ", concept_pair[0], concept_pair[1], value)
                raise e
                return None
    else:
        logger.error("no arguments for migrate_functions.map_string(). mapping: %s, value: %s", mapping, value)
        raise Exception("migrate_functions.map_string() I think your arguments list for a mapping isn't complete. Not able to map this value: {} arg:{} map:{}".format( value, arguments, mapping))

def not_null_number(value, mapping, arguments, con):
    """
        A special case of map_number using the sentinel values -1 for null and 1 for non-null to map to two concepts
          specified by argument.vocabulary_id, argument.concept_code, and return the corresponding Concept object.  
          Zero is a special case and requires a third argument. I would have given it the value for null, but the
          first time I applied this function, 0 counts as True.
        Param value is the value to map to a concept
        Param mapping is the row from study_to_ohdsi_mapping
        Param arguments, rows (in dict form)  from study_mapping_arguments that match strings to concepts
        Param con, a psycopg2 database connnection
        returns concept id for true or false
    """
    concept_pair = None
    if (arguments and len(arguments) > 0):

        int_value = None
        try:
            int_value = int(value)
        except Exception as e:
            pass

        for arg in arguments:
            if arg: 
                arg_value = None
                try:
                    arg_value = int(arg['mapped_number'])
                except Exception as e:
                    logger.error("non integer value or mapped_number. None Returned. \"%s\", \"%s\"  %s %s",
                        value, arg['mapped_number'], mapping, arguments)
                    return None

                print(" not null-->   ", arg_value, int_value)
                if int_value and int_value > 0 and arg_value == 1: 
                    # POSITIVE
                    concept_pair =  (arg['to_concept_vocabulary_id'], arg['to_concept_code'])
                elif  int_value == 0 and arg_value == 0: 
                    # ZERO
                    concept_pair =  (arg['to_concept_vocabulary_id'], arg['to_concept_code'])
                elif not int_value and arg_value == -1: 
                    # NULL
                    concept_pair =  (arg['to_concept_vocabulary_id'], arg['to_concept_code'])
            else:
                logger.error("no null arg for migrate_functions.map_number(). Check Configuration. mapping: %s, value: %s", mapping, value)

        if (not concept_pair):
            logger.error("migrate_functions.not_null_number() I think your arguments list for a mapping \
                isn't complete. It needs -1, 0, and 1. Not able to map this value: \"%s\"  arg:\"%s\" mapping:%s", 
                value, arguments, mapping)
            return None
        else:
            try:
                val = _lookup_concept_id(concept_pair[0], concept_pair[1], con)
                return val
            except Exception as e:
                logger.error("can't get concept for %s, %s", concept_pair[0], concept_pair[1])
                logger.error("exception:%s", e)
                raise e
    else:
            logger.error("migrate_functions.map_string() I think your arguments list for a mapping \
                isn't complete. Not able to map this value: \"%s\"  arg:\"%s\" mapping:%s", 
                value, arguments, mapping)
            raise Exception("migrate_functions.map_string() I think your arguments list for a mapping \
                isn't complete. Not able to map this value: \"{val}\"   \"{arg}\" {mapping}".\
                format( val=value, arg=arguments, mapping=mapping))

def not_null(value, mapping, arguments, con):
    """
        This function cares not about the type of the value, just if it is NA/None/Null or not.
        I returns false if NA, true otherwise. It requires no arguments.
        
        Param value -  the value to map to True or False concepts
        Param mapping is the row from study_to_ohdsi_mapping
        Param arguments - none expected/used
        Param con, a psycopg2 database connnection
        returns concept id for true or false
    """

    if (value is None):
        return NO_CONCEPT_ID
    else:
        return YES_CONCEPT_ID


def map_number(value, mapping, arguments, con): 
    """
        Map the passed in value from a matching argument.mapped_Number to the concept
        specified by argument.vocabulary_id, argument.concept_code, and return the corresponding Concept object.
        Param value is the value to map to a concept
        Param mapping, the driving row from study_to_ohdsi_mapping describing the destination concept location in OMOP
        Param arguments, rows (in dict form)  from study_mapping_arguments that match strings to concepts
        Param con, a psycopg2 database connnection
        returns concept_id of  vocabulary_id, concept_code of mapped value
    """
    concept_pair = None
    logger.info("migrate_functions.map_number value:%s mapping:%s", value, mapping)
    if (arguments and len(arguments) > 0):
        if value is None:
            return None

        for arg in arguments:
            if (arg) :
                #try:
                #except Exception as e:
                #    logger.error("non integer value or mapped_number. None Returned. \"%s\", \"%s\"  %s %s",
                #        value, arg['mapped_number'], mapping, arguments)
                #    return None
                int_value = None
                try:
                    int_value = int(value)
                except Exception as e:
                    pass

                try:
                    arg_value = int(arg['mapped_number'])
                except Exception as e:
                    logger.error("non integer value or mapped_number. Check configuration. None Returned. \"%s\", \"%s\"  %s %s",
                        value, arg['mapped_number'], mapping, arguments)
                    return None

                if int_value == arg_value:
                    concept_pair =  (arg['to_concept_vocabulary_id'], arg['to_concept_code'])
            else:
                logger.error("no null arg for migrate_functions.map_number(). Check Configuratin. mapping: %s, value: %s", mapping, value)
        if (not concept_pair):
            logger.error("migrate_functions.map_number() I think your arguments list for a mapping isn't complete. Not able to map this value: \"%s\"  arg:\"%s\" mapping:%s", 
                value, arguments, mapping)
            return None
        else:
            try:
                return _lookup_concept_id(concept_pair[0], concept_pair[1], con)
            except Exception as e:
                logger.error("can't get concept for %s, %s", concept_pair[0], concept_pair[1])
                logger.error("exception:%s", e)
                raise e
    else:
            logger.error("migrate_functions.map_number() I think your arguments list for a mapping isn't complete. Not able to map this value: \"%s\"  arg:\"%s\" mapping:%s", 
                value, arguments, mapping)
            raise Exception("migrate_functions.map_number() I think your arguments list for a mapping isn't complete. Not able to map this value: \"{val}\"   \"{arg}\" {mapping}".format( val=value, arg=arguments, mapping=mapping))


def map_concept(value, mapping, arguments, con): 
    """
        Param string_value
        Param mapping, the driving row from study_to_ohdsi_mapping describing the destination concept location in OMOP
        Param arguments, rows (in dict form)  from study_mapping_arguments that match strings to concepts
        Param con, a psycopg2 database connnection
        returns concept_id of mapped vocabulary_id, concpet_code pair

        ##(_, _, concept_value, map_target, _, _) 
    """

    concept_pair = None
    logger.info("migrate_functions.map_concept value:%s mapping:%s", value, mapping)
    if (arguments and len(arguments) > 0):
        if value is None:
            return None
        for arg in arguments:
            logger.info("...%s", arg)
            print(" concept -->   ", arg_value, int_value)
            if value == arg.mapped_concept:
                concept_pair =  (arg['to_concept_vocabulary_id'], arg['to_concept_code'])
        if (not concept_pair):
            logger.error("migrate_functions.map_string() I think your arguments list for a mapping isn't complete. Not able to map this value: \"%s\"  arg:\"%s\" mapping:%s", 
                value, arguments, mapping)
            return None

        else:
            return _lookup_concept_id(concept_pair[0], concept_pair[1])
    else:
            logger.error("migrate_functions.map_string() I think your arguments list for a mapping isn't complete. Not able to map this value: \"%s\"  arg:\"%s\" mapping:%s", 
                value, arguments, mapping)
            raise Exception("migrate_functions.map_string() I think your arguments list for a mapping isn't complete. Not able to map this value: \"{val}\"   \"{arg}\" {mapping}".format( val=value, arg=arguments, mapping=mapping))



def linear_equation(value, mapping, arguments, con):
    """
        Param string_value
        Param mapping, the driving row from study_to_ohdsi_mapping describing the destination concept location in OMOP
        Param arguments, 
        Param con, a psycopg2 database connnection
        returns float value
    """
    return transform(value, mapping, arguments, con)

def transform(value, mapping, arguments, con):
    """ 
        Param string_value
        Param mapping, the driving row from study_to_ohdsi_mapping describing the destination concept location in OMOP
        Param arguments, 
        Param con, a psycopg2 database connnection

        be congnizant of the shift happening AFTER the factoring, do your algebra, get it right
        Ex. f  = 9/5 * c + 32
        c = 5/9*(f-32) # not here, rather
        c = 5/9*f - 5/9*32 # so your shift value is not 32, rather 5/9*32.
    """
    if value is None:
        return None

    retval =  value * float(arguments[0]['transform_factor']) + float(arguments[0]['transform_shift'])
    logger.info("LINEAR EQUATION %s * %s +  %s :%s", str(value), str(arguments[0]['transform_factor']), str(arguments[0]['transform_shift']), str(retval))
    return retval

