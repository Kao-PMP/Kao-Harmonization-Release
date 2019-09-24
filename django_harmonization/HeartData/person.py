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
 person.py
 Python Version: 3.6.3

 migrations and mappings for BEST data to OHDSI person table
 TODO this person migration doesn't have the meta-level that the observation migration does (yet)
    - use the study table for the offset values instead of constants
    - use the study table for the prefix values instead of constants
    - ditch the STUDY_START constants? used
    - generalize the person_ids function by having teh study table tell which table to get the ids from
        also yob, gender, race
        also the  date column for table constant because anonymozation 
        also the id field name
        also date_column_for_select

 This is research code for demonstration purposes only.

 croeder 7/2017 chris.roeder@ucdenver.edu
'''

import logging
import datetime
import sys
import re
import traceback
import psycopg2
from psycopg2.extras import RealDictCursor
from abc import ABCMeta, abstractmethod
from ui.models import StudyToOhdsiMapping
from ui.models import StudyMappingArguments
from ui.models import Concept
from ui.models import Study
from HeartData import migrate_functions

##################################


UNKNOWN_ETHNICITY=2000000011 # SNOMED 10241000175103, locally entered/indexed TODO this might be in a newer version of the vocabularies

BASE_DATE="'2010-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

# TODO pull these offset constants from the db table: study

HFACTION_STUDY_START=2000 # TODO verify

##################################

UNKNOWN_RACE = 4190758 #SNOMED -4152260007

UNKNOWN_ETHNICITY=2000000011 # SNOMED 10241000175103, locally entered/indexed TODO this might be in a newer version of the vocabularies
STUDY_START=2000 # TODO verify

BEST_PERSON_ID_OFFSET=0

HFACTION_PERSON_ID_OFFSET=10000000
HFACTION_PERSON_PREFIX='HFACT'

SCDHEFT_PERSON_ID_OFFSET=11000000
SCDHEFT_PERSON_PREFIX='SCD_HEFT'
SCDHEFT_STUDY_START=2000 # TODO verify

TOPCAT_PERSON_ID_OFFSET=12000000
TOPCAT_STUDY_START=2000 # TODO verify

PARADIGM_PERSON_ID_OFFSET=13000000
PARADIGM_STUDY_START=2000 # TODO verify
ATMOSPHERE_PERSON_ID_OFFSET=14000000
ATMOSPHERE_STUDY_START=2000 # TODO verify

TEST_PERSON_ID_OFFSET=99000000
TEST_STUDY_START=2000 # TODO verify


ACCORD_STUDY_START=2000 # TODO verify
ACCORD_PERSON_ID_OFFSET =21000000

AIMHIGH_STUDY_START=2000 # TODO verify
AIMHIGH_PERSON_ID_OFFSET=22000000

ALLHAT_STUDY_START=2000 # TODO verify
ALLHAT_PERSON_ID_OFFSET =23000000

BARI2D_STUDY_START=2000 # TODO verify
BARI2D_PERSON_ID_OFFSET =24000000

logger = logging.getLogger(__name__)

class BasePerson:
    """ These classes reprensent, NOT a single patient/person/subject rather a 
        class of subjects from a particular study. Could also be thought of
        as representing the person table.
    """
    __metaclass__ = ABCMeta
    _study_id = 0


    def __init__(self, study_id):
        self._study_id = study_id


    def __str__(self):
        return "class:{0}, study_id:{1}".format(self.__class__, self._study_id);


    @abstractmethod
    def calculate_year_of_birth(self, visit_date_string, age):
        pass


    @abstractmethod
    def get_study_person_ids(self, con):
        """ returns all patients from study identified by self._study_id """
        pass


    @staticmethod
    def get_all_person_ids(con):
        """ eturns all patients in this ohdsi database regardless of study. """
        cur = con.cursor()
        cur.execute("SELECT distinct person_id FROM person")
        ids = map((lambda x: x[0]), cur.fetchall())
        cur.close()
        return ids


    @abstractmethod
    def convert_person_id_to_ohdsi(self, id) :
        """ convert from study to ohdsi """
        pass


    @abstractmethod
    def convert_person_id_to_study(self, id) :
        """ convert from ohdsi to study """
        pass


    @abstractmethod
    def populate_person(self, con):
        pass


    @staticmethod
    def factory(study):
        logger.info("BasePerson.factory() %s", study)
        logger.info("BasePerson.factory() id: %d", study.study_id)
        if (study.study_id == 1):
            thing = BESTPerson(study.study_id)
            logger.info("created BESTPerson %s", thing)
            return  thing
        elif (study.study_id >= 2 and study.study_id <=24):
            try:
                className = study.study_class
                mh = __import__("HeartData.person")  
                mp = getattr(mh, "person")
                mc = getattr(mp, className)
                thing = mc(study) 
                logger.info("created instace of class %s, %s,  %s, %s    %s", className,  mc, thing, thing._study_id, thing._study_obj)
                return  thing
            except Exception as e:
                logger.error("Person factory failed %s", study)
        else:
            logger.error("BOGUS study_id in BasePerson.factory() \"%s\" %s", study.study_id, type(study.study_id));
            return None

    @staticmethod
    def factory_on_id(study_id):
        logger.info("BasePerson.factory() %s", study_id)
        study = Study.objects.filter(study_id=study_id)[0];
        logger.info("BasePerson.factory() %s", study)

        if (study.study_id == 1 or study.study_id == 101):
            return BESTPerson(study.study_id)
        elif (study.study_id == 22):
            return AIMHIGHPerson(study)
        elif (study.study_id >= 2 and study.study_id <=24):
            try:
                className = study.study_class
                mh = __import__("HeartData.person")  
                mp = getattr(mh, "person")
                mc = getattr(mp, className)
                thing = mc(study) 
                logger.info("created instace of class %s, %s,  %s, %s    %s", className,  mc, thing, thing._study_id, thing._study_obj)
                return  thing
            except Exception as e:
                logger.error("Person factory failed %s", study)
        else:
            logger.error("BOGUS study_id in BasePerson.factory() \"%s\" %s", study.study_id, type(study.study_id));
            return None

    @abstractmethod
    def get_id_field_name(self):
        pass

    @abstractmethod
    def get_date_column_for_table(self, table_name):
        pass

    def use_date_column_on_select(self):
        return True

class TestPerson(BasePerson):
    ''' a simple class for use in tests
    '''

    def __init__(self, study_id):
        super(TestPerson, self).__init__(study_id)

    def calculate_year_of_birth(self, visit_date_string, age):
        # date string: 7/18/96 0:00
        year = re.search('\d+/\d+/(\d+)\s\d+:\d+', visit_date_string).group(1)
        if (int(year) - age > 0):
            # 2 digit year must be > 2000  TODO...
            return (int(year) - age + 100)
        else:
            # 2 digit year assume 19xx
            return int(year) - age

    def get_study_person_ids(self, con):
        return [1]

    def convert_person_id_to_ohdsi(self, id) :
        return id;

    def convert_person_id_to_study(self, id) :
        return id;

    def get_id_field_name(self):
        return "id"

    def populate_person(self, con): 
        # NO OP
        return ''

    def get_date_column_for_table(self, table_name):
        return "date_column";
    

class ParametricPerson (BasePerson):
    _study_obj = None

    def __init__(self, study_obj):
        super(ParametricPerson, self).__init__(study_obj.study_id)
        self._study_obj = study_obj
        logger.info("ParametricPerson.init() %s", self._study_obj)

    def calculate_year_of_birth(self, _, age):
        if (age is not None):
            return STUDY_START - age  
        else:
            logger.warning("age is null, assuming 0.")
            return STUDY_START

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute(self._study_obj.person_id_select)
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        if self._study_obj.person_id_prefix:
            prefix_length = len(self._study_obj.person_id_prefix)
            int_id = int(id[prefix_length:])
        else:
            int_id = int(id)
        return str(int_id + self._study_obj.person_id_range_start)

    def convert_person_id_to_study(self, id) : 
        int_id = int(id) - self._study_obj.person_id_range_start
        if (self._study_obj.person_id_prefix):
            return str(self._study_obj.person_id_prefix) + str(int_id)
        else:
            return str(int_id)

    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        logger.info("ParametricPerson.populate_person study: %s, sex table: %s, sex column %s, sex function: %s",
            self._study_obj.study_id, self._study_obj.sex_table_name, self._study_obj.sex_column_name, self._study_obj.sex_function_name)

        # need to fetch the mappings for gender and race since we're parametric now
        gender_mapping = None
        try:
            gender_mapping = StudyToOhdsiMapping.objects.filter(
                study_id=self._study_obj.study_id,
                from_table=self._study_obj.sex_table_name,
                from_column=self._study_obj.sex_column_name,
                function_name=self._study_obj.sex_function_name).values()
        except Exception as e:
            logger.error("ERROR querying StudyToOhdsiMapping %s %s %s %s", self._study_obj.study_id, 
                self._study_obj.sex_table_name, self._study_obj.sex_column_name, self._study_obj.sex_function_name)
            logger.warning(" *** compare your person mapping details with those in StudyToOhdsiMapping ")
            raise e
        logger.info("person.populate_person() gender mapping %s", gender_mapping)
        if (gender_mapping is None) :
            logger.error("HeartData.person.populate_person() requires there be a concept mapping for gender in study_to_ohdsi_mappings for the keys study_id:%s, from_table:%s, from_column:%s, function_name:%s", 
                self._study_obj.study_id, self._study_obj.sex_table_name, self._study_obj.sex_column_name,
                self._study_obj.sex_function_name)
        race_mapping=None
        try:
            if (self._study_obj.race_column_name is not None):
                race_mapping = StudyToOhdsiMapping.objects.filter(
                    study_id=self._study_obj.study_id,
                    from_table=self._study_obj.race_table_name,
                    from_column=self._study_obj.race_column_name,
                    function_name=self._study_obj.race_function_name).values()
        except Exception as e:
            logger.error("Not able to filter StudyToOhdsiMapping %s %s %s %s", 
                self._study_obj.study_id, self._study_obj.race_table_name, 
                self._study_obj.race_column_name, self._study_obj.race_function_name)
            logger.error("   This can mean that the configurations in the study table don't align with those in study_to_ohdsi_mapping.")
            raise e
        logger.info("person.populate_person() race mapping %s", race_mapping)
        if (race_mapping is None) :
            logger.error("HeartData.person.populate_person() requires there be a concept mapping for gender in study_to_ohdsi_mappings for the keys study_id:%s, from_table:%s, from_column:%s, function_name:%s", 
                self._study_obj.study_id, self._study_obj.race_table_name, self._study_obj.race_column_name,
                self._study_obj.race_function_name)

        gender_map_arguments = StudyMappingArguments.objects.filter(
            study_id=self._study_obj.study_id,
            from_table=self._study_obj.sex_table_name,
            from_column=self._study_obj.sex_column_name,
            function_name=self._study_obj.sex_function_name).values()
        race_map_arguments = None
        if (race_mapping):
            race_map_arguments = StudyMappingArguments.objects.filter(
                study_id=self._study_obj.study_id,
                from_table=self._study_obj.race_table_name,
                from_column=self._study_obj.race_column_name,
                function_name=self._study_obj.race_function_name).values()
        # Consider these two queries that populate this stuff from the mappings for sex and race:
        # (depends on using the concepts specified...)
        ## update  study 
        ##   set  race_table_name = m.from_table,  race_column_name = m.from_column, race_function_name = m.function_name 
        ##   from study_to_ohdsi_mapping m 
        ##   where m.concept_code = '103579009' and study.study_id = m.study_id;
        ## update  study 
        ##   set  sex_table_name = m.from_table,  sex_column_name = m.from_column, sex_function_name = m.function_name 
        ##   from study_to_ohdsi_mapping m 
        ##   where m.concept_code = '263495000' and study.study_id = m.study_id;

        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        logger.info("select details: %s", self._study_obj.person_details_select)
        rows=[]
        try:
            cur.execute(self._study_obj.person_details_select)
            # id, visit, sex, age, race
            rows = cur.fetchall()
        except Exception as e:
            logger.error("person.populate_person() error selecting person details %s \n  exception:%s", self._study_obj.person_details_select, e)
            raise e
        for row in rows:
            logger.info("PERSON.populate_person() ROW:%s id:%s", row[0], row)
            stmt_string=""
            race=0
            try:
                person_id = self.convert_person_id_to_ohdsi(row[0]) 
                yob =  self.calculate_year_of_birth("", row[3])
              
                # GENDER 
                if (gender_map_arguments[0]['function_name'] == 'map_number'):
                    gender_concept_id = migrate_functions.map_number(row[2],  gender_mapping, gender_map_arguments, con)
                elif (gender_map_arguments[0]['function_name'] == 'map_string'):
                    gender_concept_id = migrate_functions.map_string(row[2],  gender_mapping, gender_map_arguments, con)
                else:
                    logger.error("unknown function in person.populate_person() %s", gender_map_arguments[0].function_name)
                if (gender_concept_id is None) :
                    logger.error("NO GENDER MAPPING %s %s", row, gender_mapping)
                    for gma in gender_map_arguments:
                        logger.error("gender mapping argument %s", gma)

                 # relevant shape of the map_arguments
                 #(string_value, _, _, map_target, _, _)
                 #(_, number_value, _, map_target, _, _)

                # RACE
                race_concept_id = UNKNOWN_RACE
                if (race_map_arguments is not None and len(race_map_arguments) >0):
                    if (race_map_arguments[0]['function_name'] == 'map_number'):
                        race_concept_id = migrate_functions.map_number(row[4], race_mapping, race_map_arguments, con)
                    elif (race_map_arguments[0]['function_name'] == 'map_string'):
                        race_concept_id = migrate_functions.map_string(row[4], race_mapping, race_map_arguments, con)
                    else:
                        logger.error("unknown function in person.populate_person() %s", race_map_arguments[0].function_name)
                    if (race_concept_id is None) :
                        race_concept_id = UNKNOWN_RACE
                        logger.error("NO RACE MAPPING {%s} {%s}, using unknown race", row, race_mapping)
                        for gma in race_map_arguments:
                            logger.error("race mapping argument %s", gma)
    
                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race_concept_id, UNKNOWN_ETHNICITY)) # TODO ethnicity
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                traceback.print_tb(e.__traceback__)
                raise e
        cur.close()
        con.commit()
        logger.info("done populating.")

   
    def get_id_field_name(self):
        return self._study_obj.id_field_name;
    
    def get_date_column_for_table(self, table_name):
        return BASE_DATE

    def use_date_column_on_select(self):
        return False

class AIMHIGHPerson (ParametricPerson):
    def __init__(self, study_id):
        super(AIMHIGHPerson, self).__init__(study_id)

    def get_date_column_for_table(self, table_name):
        if (table_name == 'aimhigh.LAB') :
            return "visit"
        else:
            return BASE_DATE 

    def use_date_column_on_select(self):
        return True

class BESTPerson(ParametricPerson):

    def __init__(self, study_id):
        super(BESTPerson, self).__init__(study_id)
        logger.info("BestPerson.__init__(): %d %d", study_id, self._study_id)

    def calculate_year_of_birth(self, visit_date_string, age):
        # date string: 7/18/96 0:00
        year = re.search('\d+/\d+/(\d+)\s\d+:\d+', visit_date_string).group(1)
        if (int(year) - age > 0):
            # 2 digit year must be > 2000  TODO...
            return (int(year) - age + 100)
        else:
            # 2 digit year assume 19xx
            return int(year) - age


    ##def populate_person(self, con): 
    ##            ethnicity = best_ethnicity_to_concept(row['pcrace'])
    ##            stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id)" 


    def get_date_column_for_table(self, table_name):
        date_column_name = "visit_dt"
        if (table_name == 'best.br') :
            date_column_name = "vdate"
        elif (table_name == 'best.eos') :
            date_column_name = "vdate"
        elif (table_name == 'best.mort1'):
            date_column_name = 'modate'
        elif (table_name == 'best.adju'):
            date_column_name = 'addate' # TODO, this is date of death, not adjudication. May matter depending on the column. Just record this fact?
        return date_column_name

