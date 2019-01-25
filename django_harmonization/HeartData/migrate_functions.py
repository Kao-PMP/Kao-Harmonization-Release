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

 croeder 7/2017 chris.roeder@ucdenver.edu
'''

import sys
import re
import psycopg2
import psycopg2.extras
import logging
import string
from . import person

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

from HeartData.concepts import SMOKE_NEVER_CONCEPT_ID
from HeartData.concepts import SMOKE_CURRENT_CONCEPT_ID
from HeartData.concepts import SMOKE_SMOKELESS_CONCEPT_ID
from HeartData.concepts import SMOKE_FORMER_CONCEPT_ID
from HeartData.concepts import BARI2D_RACE_1_CONCEPT_ID
from HeartData.concepts import BARI2D_RACE_2_CONCEPT_ID


logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

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

def paradigm_yes_no_to_concept(tc_yes_no):
    if tc_yes_no == P_YES:
        return YES_CONCEPT_ID
    else:
        return NO_CONCEPT_ID

def atmosphere_yes_no_to_concept(tc_yes_no):
    if tc_yes_no == P_YES:
        return YES_CONCEPT_ID
    else:
        return NO_CONCEPT_ID

def sex_to_concept_m0f1(sex):
    if sex == 0:
        return MALE_CONCEPT_ID
    elif sex == 1:
        return FEMALE_CONCEPT_ID
    else:
        return None

def sex_to_concept_f0m1(sex):
    if sex == 0:
        return FEMALE_CONCEPT_ID
    elif sex == 1:
        return MALE_CONCEPT_ID
    else:
        return None

def sex_to_concept_m1f2(sex):
    if sex == 1:
        return MALE_CONCEPT_ID
    elif sex == 2:
        return FEMALE_CONCEPT_ID
    else:
        return None

def paradigm_sex_to_concept(tc_sex):
    if tc_sex == P_MALE:
        return MALE_CONCEPT_ID
    elif tc_sex == P_FEMALE:
        return FEMALE_CONCEPT_ID
    else:
        return None

def atmosphere_sex_to_concept(tc_sex):
    if tc_sex == P_MALE:
        return MALE_CONCEPT_ID
    elif tc_sex == P_FEMALE:
        return FEMALE_CONCEPT_ID
    else:
        return None

def paradigm_race_to_concept(race):
    if race == P_AFRICAN_AMERICAN:
        return AFRICAN_AMERICAN_CONCEPT_ID
    elif race == P_CAUCASIAN:
        return CAUCASIAN_CONCEPT_ID
    elif race == P_ASIAN:
        return ASIAN_CONCEPT_ID
    elif race == P_OTHER:
        return OTHER_RACE_CONCEPT_ID
    else:
        return None

def aimhigh_race_to_concept(race):
    if race == AIMHIGH_OTHER_RACE:
            return OTHER_RACE_CONCEPT_ID
    if race == AIMHIGH_WHITE_RACE:
            return CAUCASIAN_CONCEPT_ID
    if race == AIMHIGH_BLACK_RACE:
            return AFRICAN_AMERICAN_CONCEPT_ID
    if race == AIMHIGH_ASIAN_RACE:
            return ASIAN_CONCEPT_ID
    if race == AIMHIGH_AM_INDIAN_RACE:
           return AMERICAN_INDIAN_CONCEPT_ID
    else:
           return None

def aimhigh_smoke_to_concept(smoke):
    if smoke == AIMHIGH_SMOKE_NEVER:
        return SMOKE_NEVER_CONCEPT_ID
    if smoke == AIMHIGH_SMOKE_CURRENT:
        return SMOKE_CURRENT_CONCEPT_ID
    if smoke == AIMHIGH_SMOKELESS:
        return SMOKE_SMOKELESS_CONCEPT_ID
    if smoke == AIMHIGH_SMOKE_FORMER:
        return SMOKE_FORMER_CONCEPT_ID
    else:
        return None

def atmosphere_race_to_concept(race):
    if race == P_AFRICAN_AMERICAN:
        return AFRICAN_AMERICAN_CONCEPT_ID
    elif race == P_CAUCASIAN:
        return CAUCASIAN_CONCEPT_ID
    elif race == P_ASIAN:
        return ASIAN_CONCEPT_ID
    elif race == P_OTHER:
        return OTHER_RACE_CONCEPT_ID
    else:
        return None


def topcat_yes_no_to_concept(tc_yes_no):
    if tc_yes_no == TC_YES:
        return YES_CONCEPT_ID
    elif tc_yes_no == TC_NO:
        return NO_CONCEPT_ID
    else:
        return None

def topcat_sex_to_concept(tc_sex):
    if tc_sex == TC_MALE:
        return MALE_CONCEPT_ID
    elif tc_sex == TC_FEMALE:
        return FEMALE_CONCEPT_ID
    else:
        return None

def topcat_race_to_concept(race):
    if race == TC_AFRICAN_AMERICAN:
        return AFRICAN_AMERICAN_CONCEPT_ID
    elif race == TC_CAUCASIAN:
        return CAUCASIAN_CONCEPT_ID
    elif race == TC_ASIAN:
        return ASIAN_CONCEPT_ID
    elif race == TC_OTHER:
        return OTHER_RACE_CONCEPT_ID
    else:
        return None


def scdheft_yes_no_to_concept(sh_yes_no):
    if sh_yes_no == SH_YES:
        return YES_CONCEPT_ID
    elif sh_yes_no == SH_NO:
        return NO_CONCEPT_ID
    else:
        return None

def scdheft_sex_to_concept(sh_sex):
    if sh_sex == SH_MALE:
        return MALE_CONCEPT_ID
    elif sh_sex == SH_FEMALE:
        return FEMALE_CONCEPT_ID
    else:
        return None

def scdheft_race_to_concept(race):
    if race == SH_AFRICAN_AMERICAN:
        return AFRICAN_AMERICAN_CONCEPT_ID
    elif race == SH_CAUCASIAN:
        return CAUCASIAN_CONCEPT_ID
    elif race == SH_ASIAN:
        return ASIAN_CONCEPT_ID
#    elif race == SH_NATIVE_AMERICAN:
#        return AMERICAN_INDIAN_CONCEPT_ID
#    elif race == SH_PACIFIC_ISLANDER:
#        return PACIFIC_ISLANDER_CONCEPT_ID
    elif race == SH_LATIN_AMERICAN:
        return HISPANIC_CONCEPT_ID
    elif race == SH_OTHER:
        return OTHER_RACE_CONCEPT_ID
    else:
        return None

def scdheft_btx_to_placebo(btx):
    if (btx == 1): # has 829 here. These are the ICDs.
        return NO_CONCEPT_ID # HAS and ICD, is NOT the placebo
    elif (btx == 2): # has 1692 of these
        return YES_CONCEPT_ID
    else:
        return None

def hfaction_yes_no_to_concept(hf_yes_no):
    if hf_yes_no == HF_YES:
        return YES_CONCEPT_ID
    elif hf_yes_no == HF_NO:
        return NO_CONCEPT_ID
    else:
        return None

def hfaction_yes_no_to_concept12(hf_yes_no):
    if hf_yes_no == HF_YES_12:
        return YES_CONCEPT_ID
    elif hf_yes_no == HF_NO_12:
        return NO_CONCEPT_ID
    else:
        return None

def hfaction_sex_to_concept(hf_sex):
    if hf_sex == HF_MEN:
        return MALE_CONCEPT_ID
    elif hf_sex == HF_WOMEN:
        return FEMALE_CONCEPT_ID
    else:
        return None

def hfaction_race_to_concept(race):
    if race == HF_AFRICAN_AMERICAN:
        return AFRICAN_AMERICAN_CONCEPT_ID
    elif race == HF_CAUCASIAN:
        return CAUCASIAN_CONCEPT_ID
    elif race == HF_ASIAN:
        return ASIAN_CONCEPT_ID
    elif race == HF_AMERICAN_INDIAN:
        return AMERICAN_INDIAN_CONCEPT_ID
    elif race == HF_PACIFIC_ISLANDER:
        return PACIFIC_ISLANDER_CONCEPT_ID
    else:
        return None



def best_sex_to_concept(best_sex):
    """ Maps the value, work in concert with a mapping in study_to_ohdsi_mapping
       that specifies the destination vocabulary and concept_code. The value's term
       is in the same vocabulary and calculated here.
    """
    # concept: SNOMED 263495000
    # value: Female       |   703118005 | SNOMED         | Answer
    # value: Male         |   703111700 | SNOMED         | Answer
    if best_sex == BEST_MALE:
        return 45766034 #703117000  # male
    elif best_sex == BEST_FEMALE:
        return 45766035 #703118005  # female
    else:
        return None

def best_yes_no_to_concept(best_yes_no):
    if (best_yes_no == None):
        logger.error("migrate_functions.best_yes_no_to_concept() got a None input value!")        

    if best_yes_no == BEST_YES:
        return YES_CONCEPT_ID
    elif best_yes_no == BEST_NO:
        return NO_CONCEPT_ID
    else:
        None

def aimhigh_race_to_concept(best_race):
    return CAUCASIAN_CONCEPT_ID # TODO

def accord_race_to_concept(race):
    if (race == 'Black'):
        return AFRICAN_AMERICAN_CONCEPT_ID
    elif (race == 'White'):
        return CAUCASIAN_CONCEPT_ID
    elif (race == 'Other'):
        return OTHER_RACE_CONCEPT_ID
    elif (race == 'Hispanic'):
        return HISPANIC_CONCEPT_ID
    return CAUCASIAN_CONCEPT_ID # TODO

def bari2d_race_to_concept(race):
    if (race == 1):
        return BARI2D_RACE_1_CONCEPT_ID
    if (race == 2):
        return BARI2D_RACE_2_CONCEPT_ID


def best_race_to_concept(best_race):
    # value: African American   SNOMED 15086000
    # value: Caucasian          SNOMED 413773004
    # value: hispanic           SNOMED 414408004
    # value: asian              SNOMED 413582008
    # value: native am.         SNOMED 413490006
    # value: other ?
    # concept:  SNOMED Race          | 103579009
    # BEST: 1:White, 2:Black, 3:Hispanic, 4:Asian, 5:Native Am., 6:Other
    race_mapping = {1:4185154, 2:4035165, 3:4188159, 4:4211353, 5:4184966, 6:0}
    return race_mapping[best_race]

def best_ethnicity_to_concept(best_race):
    # value: Hispanic or Latino     |   38003563 | Ethnicity     | Ethnicity
    # value: Not Hispanic or Latino |   38003564 | Ethnicity     | Ethnicity
    # OHDSI concept ids from a standard concept, no particular vocabulary?
    ethnicity_mapping = { 1:38003564, 2:38003564, 3:38003563, 4:38003564, 5:38003564, 6:38003564}
    return ethnicity_mapping[best_race]


# ----- GENERIC --------

def string_yes_no_to_concept(best_yes_no):
    if best_yes_no == 'yes':
        return YES_CONCEPT_ID
    elif best_yes_no == 'no':
        return NO_CONCEPT_ID
    else:
        logger.error("string_yes_no_to_concept() unknown \"%s\"", best_yes_no)
        #return NO_CONCEPT_ID
        return None;

def yes_no_to_concept(yes_no):
    try:
        yes_no_int = int(yes_no)
    except:
        return None
    if yes_no_int == 1:
        return YES_CONCEPT_ID
    elif yes_no_int == 0:
        return NO_CONCEPT_ID
    else:
        logger.error("yes_no_to_concept() unknown \"%s\"", yes_no)
        return None # NO_CONCEPT_ID   #TODO

def yes_no_to_concept_12(yes_no):
    if yes_no == 1:
        return YES_CONCEPT_ID
    elif yes_no == 2:
        return NO_CONCEPT_ID
    else:
        logger.error("yes_no_to_concept_12() unknown \"%s\"", yes_no)
        return None;
        #return NO_CONCEPT_ID

def cm_to_in(cm):
    return cm / 2.54

def kg_to_lb(kg):
    return kg * 2.2

def decimal_to_percent(dec):
    return dec * 100

def years_to_months(years):
    return years * 12

def years_to_days(years):
    return years * 365

def true(_):
    return YES_CONCEPT_ID

def centiseconds_to_milliseconds(cs):
    return cs * 10




