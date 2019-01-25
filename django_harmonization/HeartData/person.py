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
import psycopg2
from psycopg2.extras import RealDictCursor
from abc import ABCMeta, abstractmethod

from HeartData.migrate_functions import sex_to_concept_m0f1
from HeartData.migrate_functions import sex_to_concept_f0m1
from HeartData.migrate_functions import sex_to_concept_m1f2

from HeartData.migrate_functions import best_sex_to_concept
from HeartData.migrate_functions import best_ethnicity_to_concept
from HeartData.migrate_functions import best_race_to_concept

from HeartData.migrate_functions import hfaction_sex_to_concept
from HeartData.migrate_functions import hfaction_race_to_concept

from HeartData.migrate_functions import scdheft_sex_to_concept
from HeartData.migrate_functions import scdheft_race_to_concept

from HeartData.migrate_functions import topcat_sex_to_concept
from HeartData.migrate_functions import topcat_race_to_concept

from HeartData.migrate_functions import paradigm_sex_to_concept
from HeartData.migrate_functions import paradigm_race_to_concept

from HeartData.migrate_functions import atmosphere_sex_to_concept
from HeartData.migrate_functions import atmosphere_race_to_concept

from HeartData.migrate_functions import accord_race_to_concept
from HeartData.migrate_functions import aimhigh_race_to_concept
from HeartData.migrate_functions import bari2d_race_to_concept


UNKNOWN_ETHNICITY=2000000011 # SNOMED 10241000175103, locally entered/indexed TODO this might be in a newer version of the vocabularies

# TODO pull these offset constants from the db table: study
BEST_PERSON_ID_OFFSET=0

HFACTION_PERSON_ID_OFFSET=10000000
HFACTION_PERSON_PREFIX='HFACT'
HFACTION_STUDY_START=2000 # TODO verify

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

logging.basicConfig(level=logging.INFO)
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
    def factory(study_id):
        if (study_id == 1):
            return BESTPerson(study_id)
        elif (study_id == 2):
            return HFACTIONPerson(study_id)
        elif (study_id == 3):
            return SCDHEFTPerson(study_id)
        elif (study_id == 4):
            return TOPCATPerson(study_id)
        elif (study_id == 5):
            return PARADIGMPerson(study_id)
        elif (study_id == 10):
            return TESTPerson(study_id)
        elif (study_id == 21):
            return ACCORDPerson(study_id)
        elif (study_id == 22):
            return AIMHIGHPerson(study_id)
        elif (study_id == 23):
            return ALLHATPerson(study_id)
        elif (study_id == 24):
            return BARI2DPerson(study_id)
        else:
            logger.error("BOGUS study_id in BasePerson.factory() \"%s\" %s", study_id, type(study_id));
            return None

    @abstractmethod
    def get_id_field_name(self):
        pass

    @abstractmethod
    def get_date_column_for_table(self, table_name):
        pass

    def use_date_column_on_select(self):
        return True


class BESTPerson(BasePerson):

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


    def get_study_person_ids(self, con):
        """ Returns distinct person IDs from the PCSF dataset in ohdsi form. For BEST, the ohdsi form of the person id is the same.. """
        cur = con.cursor()
        cur.execute("SELECT distinct id FROM best.pcsf")
        ids = map(lambda x: self.convert_person_id_to_ohdsi(x[0]), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) :
        return id

    def convert_person_id_to_study(self, id) :
        return id

    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        """Populates the OHDSI person table from values extracted by the pcsf dataset.
        Also returns a list of person IDs useful later.
        """

        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, visit_dt, pcsex, pcage, pcrace FROM best.pcsf")
        rows = cur.fetchall()
        for row in rows:
            stmt_string=""
            try:
                id = row['id']
                yob =  self.calculate_year_of_birth(row['visit_dt'], row['pcage'])
                gender_id = best_sex_to_concept(row['pcsex'])
                race = best_race_to_concept(row['pcrace'])
                ethnicity = best_ethnicity_to_concept(row['pcrace'])
                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id)" 
                     "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (id, gender_id, yob, race, ethnicity))
            except Exception as e:
                logger.error("populate_person():%s %s %s", row, stmt_string, e)
                raise
        cur.close()
        con.commit()

    def get_id_field_name(self):
        return "id"

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


class HFACTIONPerson (BasePerson):

    def __init__(self, study_id):
        super(HFACTIONPerson, self).__init__(study_id)
        logger.info("HfactionPerson.__init__(): %d %d", study_id, self._study_id)

    def calculate_year_of_birth(self, _, age):
        return HFACTION_STUDY_START - age # crude estimate since we don't have DOB or the date of randomization since the data is anonymized:TODO

    def get_study_person_ids(self, con):
        """ Returns distinct person IDs from the PCSF dataset in the ohdsi format. For HF-ACTION that means peeling off the prefix and offsetting the values to make room for best. """
        cur = con.cursor()
        cur.execute("SELECT distinct newid FROM hfaction.analysis")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall())
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, hf_id) :
        """ convert from hfaction to ohdsi """
        return int(hf_id[len(HFACTION_PERSON_PREFIX):]) + HFACTION_PERSON_ID_OFFSET

    def convert_person_id_to_study(self, hf_id) :
        """ convert from ohdsi to hfaction """
        return "{pre}{num:05d}".format(pre=HFACTION_PERSON_PREFIX, num=(hf_id - HFACTION_PERSON_ID_OFFSET))

    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        """Populates the OHDSI person table from values extracted by the pcsf dataset.
        Also returns a list of person IDs useful later.
        """

        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT newid, age, gender, racec FROM hfaction.analysis")
        rows = cur.fetchall()
        for row in rows:
            stmt_string=""
            try:
                hfaction_id = row['newid']
                person_id = self.convert_person_id_to_ohdsi(hfaction_id)
                yob =  self.calculate_year_of_birth("", row['age'])
                gender_concept_id = hfaction_sex_to_concept(row['gender'])
                race = hfaction_race_to_concept(row['racec'])
                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s %s", row, stmt_string, e)
                raise
        cur.close()
        con.commit()


    def get_id_field_name(self):
        return "newid"

    def get_date_column_for_table(self, table_name):
        return "'2015-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

class SCDHEFTPerson (BasePerson):
    # randomization form is from 12/10/1998

    def __init__(self, study_id):
        super(SCDHEFTPerson, self).__init__(study_id)
        logger.info("ScdheftPerson.__init__(): %d %d", study_id, self._study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return SCDHEFT_STUDY_START - age # crude estimate since we don't have DOB or the date of randomization since the data is anonymized:TODO

    def get_study_person_ids(self, con):
        """ Returns distinct person IDs from the PCSF dataset in the ohdsi format. For HF-ACTION that means peeling off the prefix and offsetting the values to make room for best. """
        cur = con.cursor()
        cur.execute("SELECT distinct pid FROM scdheft.basecrf")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall())
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) :
        """ convert from ohdsi to SCD-HeFT """
        return int(id[len(SCDHEFT_PERSON_PREFIX):]) + SCDHEFT_PERSON_ID_OFFSET

    def convert_person_id_to_study(self, id) :
        """ convert from ohdsi to SCD-HeFT """
        return "{pre}{num:04d}".format(pre=SCDHEFT_PERSON_PREFIX, num=(id - SCDHEFT_PERSON_ID_OFFSET))


    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.

        cur = con.cursor()
        cur.execute("SELECT b.pid, b.age, b.gender, r.race_redact FROM scdheft.baseline_new b, scdheft.rdemog r where r.pid = b.pid")
        rows = cur.fetchall()
        for row in rows:
            print("populate_person() ROW:", row)
            stmt_string=""
            try:
                scdheft_id = row[0]
                person_id = self.convert_person_id_to_ohdsi(scdheft_id)
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = scdheft_sex_to_concept(row[2])
                race = scdheft_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) "
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s %s", row, stmt_string, e)
                raise
        cur.close()
        con.commit()

    def get_id_field_name(self):
        return "pid"

    def get_date_column_for_table(self, table_name):
        return "'2000-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

class TOPCATPerson (BasePerson):

    def __init__(self, study_id):
        super(TOPCATPerson, self).__init__(study_id)
        logger.info("TopcatPerson.__init__(): %d %d", study_id, self._study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return TOPCAT_STUDY_START - age # crude estimate since we don't have DOB or the date of randomization since the data is anonymized:TODO

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute("SELECT distinct id FROM topcat.t003")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        """ convert from ohdsi to TOPCAT """
        return id + TOPCAT_PERSON_ID_OFFSET 

    def convert_person_id_to_study(self, id) : 
        """ convert from ohdsi to TOPCAT """
        return id - TOPCAT_PERSON_ID_OFFSET


    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.

        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        cur.execute("SELECT t.id, t.age_entry, t.gender, t.race_cat * (1 - t.race_other) + t.race_other * 4 FROM topcat.t003 t")
        rows = cur.fetchall()
        for row in rows:
            print("populate_person() ROW:", row)
            stmt_string=""
            try:
                id = row[0]
                person_id = self.convert_person_id_to_ohdsi(id) 
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = topcat_sex_to_concept(row[2])
                race = topcat_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                raise
        cur.close()
        con.commit()
   
    def get_id_field_name(self):
        return "id"
    
    def get_date_column_for_table(self, table_name):
        return "'2000-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

    def use_date_column_on_select(self):
        return False

class PARADIGMPerson (BasePerson):

    def __init__(self, study_id):
        super(PARADIGMPerson, self).__init__(study_id)
        logger.info("ParadigmPerson.__init__(): %d %d", study_id, self._study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return PARADIGM_STUDY_START - age  # anonymozation leaves us with no data, use a constant with no effort to estimate

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute("SELECT distinct index FROM paradigm.test")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        """ convert from ohdsi to PARADIGM"""
        return id + PARADIGM_PERSON_ID_OFFSET 

    def convert_person_id_to_study(self, id) : 
        """ convert from ohdsi to PARADIGM """
        return id - PARADIGM_PERSON_ID_OFFSET


    # *** TODO *** 
    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        cur.execute("SELECT t.index, t.age_1n, t.sex1c, t.race  FROM paradigm.test t")
        rows = cur.fetchall()
        for row in rows:
            print("populate_person() ROW:", row)
            stmt_string=""
            race=0
            try:
                person_id = self.convert_person_id_to_ohdsi(row[0]) 
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = paradigm_sex_to_concept(row[2])
                race = paradigm_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                raise
        cur.close()
        con.commit()
   
    def get_id_field_name(self):
        return "index"
    
    def get_date_column_for_table(self, table_name):
        return "'2010-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

    def use_date_column_on_select(self):
        return False

class ATMOSPHEREPerson (BasePerson):

    def __init__(self, study_id):
        super(ATMOSPHEREPerson, self).__init__(study_id)
        logger.info("AtmospherePerson.__init__(): %d %d", study_id, self._study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return ATMOSPHERE_STUDY_START - age  # anonymozation leaves us with no data, use a constant with no effort to estimate

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute("SELECT distinct index FROM atmosphere.test")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        """ convert from ohdsi to ATMOSPHERE"""
        return id + ATMOSPHERE_PERSON_ID_OFFSET 

    def convert_person_id_to_study(self, id) : 
        """ convert from ohdsi to ATMOSPHERE """
        return id - ATMOSPHERE_PERSON_ID_OFFSET


    # *** TODO *** 
    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        cur.execute("SELECT t.index, t.age_1n, t.sex1c, t.race  FROM atmosphere.test t")
        rows = cur.fetchall()
        for row in rows:
            print("populate_person() ROW:", row)
            stmt_string=""
            race=0
            try:
                person_id = self.convert_person_id_to_ohdsi(row[0]) 
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = atmosphere_sex_to_concept(row[2])
                race = atmosphere_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                raise
        cur.close()
        con.commit()
   
    def get_id_field_name(self):
        return "index"
    
    def get_date_column_for_table(self, table_name):
        return "'2010-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

    def use_date_column_on_select(self):
        return False

class TESTPerson (BasePerson):

    def __init__(self, study_id):
        super(TESTPerson, self).__init__(study_id)
        logger.info("TestPerson.__init__(): %d %d", study_id, self._study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return TEST_STUDY_START - age  # anonymozation leaves us with no data, use a constant with no effort to estimate

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute("SELECT distinct person_id FROM test.data")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        """ convert from ohdsi to TEST"""
        print("TEST id", id, id + TEST_PERSON_ID_OFFSET)
        return id + TEST_PERSON_ID_OFFSET 

    def convert_person_id_to_study(self, id) : 
        """ convert from ohdsi to ATMOSPHERE """
        print("TEST id", id, id - TEST_PERSON_ID_OFFSET)
        return id - TEST_PERSON_ID_OFFSET


    # *** TODO *** 
    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        cur.execute("SELECT t.person_id, t.age, t.sex, t.race  FROM test.data t")
        rows = cur.fetchall()
        for row in rows:
            logger.info("PERSON.populate_person() ROW:%s id:%s", row[0], row)
            stmt_string=""
            race=0
            try:
                person_id = self.convert_person_id_to_ohdsi(row[0]) 
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = best_sex_to_concept(row[2])
                race = atmosphere_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                raise
        cur.close()
        con.commit()
   
    def get_id_field_name(self):
        return "person_id"
    
    def get_date_column_for_table(self, table_name):
        return "'2010-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

    def use_date_column_on_select(self):
        return False


class ACCORDPerson (BasePerson):

    def __init__(self, study_id):
        super(ACCORDPerson, self).__init__(study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return ACCORD_STUDY_START - age  # anonymozation leaves us with no data, use a constant with no effort to estimate

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute("SELECT distinct maskid FROM accord.\"ACCORD_KEY\"")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        """ convert from ohdsi to TEST"""
        return id + ACCORD_PERSON_ID_OFFSET 

    def convert_person_id_to_study(self, id) : 
        """ convert from ohdsi to ATMOSPHERE """
        return id - ACCORD_PERSON_ID_OFFSET


    # *** TODO *** 
    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        cur.execute("SELECT t.maskid, t.baseline_age, t.female, t.raceclass  FROM accord.\"ACCORD_KEY\" t")
        rows = cur.fetchall()
        for row in rows:
            logger.info("PERSON.populate_person() ROW:%s id:%s", row[0], row)
            stmt_string=""
            race=0
            try:
                person_id = self.convert_person_id_to_ohdsi(row[0]) 
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = sex_to_concept_m0f1(row[2])
                race = accord_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                raise
        cur.close()
        con.commit()
   
    def get_id_field_name(self):
        return "maskid"
    
    def get_date_column_for_table(self, table_name):
        return "'2010-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

    def use_date_column_on_select(self):
        return False

class AIMHIGHPerson (BasePerson):
    def __init__(self, study_id):
        super(AIMHIGHPerson, self).__init__(study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return AIMHIGH_STUDY_START - age  # anonymozation leaves us with no data, use a constant with no effort to estimate

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute("SELECT distinct patientkey FROM aimhigh.\"PATIENT\"")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        """ convert from ohdsi to TEST"""
        return id + AIMHIGH_PERSON_ID_OFFSET 

    def convert_person_id_to_study(self, id) : 
        """ convert from ohdsi to ATMOSPHERE """
        return id - AIMHIGH_PERSON_ID_OFFSET


    # *** TODO *** 
    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        cur.execute("SELECT t.patientkey, t.age, t.sex, t.race FROM aimhigh.\"PATIENT\" t")
        rows = cur.fetchall()
        for row in rows:
            logger.info("PERSON.populate_person() ROW:%s id:%s", row[0], row)
            stmt_string=""
            race=0
            try:
                person_id = self.convert_person_id_to_ohdsi(row[0]) 
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = sex_to_concept_f0m1(row[2])
                race = aimhigh_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                raise
        cur.close()
        con.commit()
   
    def get_id_field_name(self):
        return "patientkey"
    
    def get_date_column_for_table(self, table_name):
        return "'2010-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

    def use_date_column_on_select(self):
        return False

class ALLHATPerson (BasePerson):
    def __init__(self, study_id):
        super(ALLHATPerson, self).__init__(study_id)
        logger.info("TestPerson.__init__(): %d %d", study_id, self._study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return TEST_STUDY_START - age  # anonymozation leaves us with no data, use a constant with no effort to estimate

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute("SELECT distinct person_id FROM test.data")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        """ convert from ohdsi to TEST"""
        print("TEST id", id, id + ALLHAT_PERSON_ID_OFFSET)
        return id + ALLHAT_PERSON_ID_OFFSET 

    def convert_person_id_to_study(self, id) : 
        """ convert from ohdsi to ATMOSPHERE """
        print("TEST id", id, id - ALLHAT_PERSON_ID_OFFSET)
        return id - ALLHAT_PERSON_ID_OFFSET


    # *** TODO *** 
    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        cur.execute("SELECT t.person_id, t.age, t.sex, t.race  FROM test.data t")
        rows = cur.fetchall()
        for row in rows:
            logger.info("PERSON.populate_person() ROW:%s id:%s", row[0], row)
            stmt_string=""
            race=0
            try:
                person_id = self.convert_person_id_to_ohdsi(row[0]) 
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = best_sex_to_concept(row[2])
                race = atmosphere_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                raise
        cur.close()
        con.commit()
   
    def get_id_field_name(self):
        return "person_id"
    
    def get_date_column_for_table(self, table_name):
        return "'2010-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

    def use_date_column_on_select(self):
        return False

class BARI2DPerson (BasePerson):
    def __init__(self, study_id):
        super(BARI2DPerson, self).__init__(study_id)

    # ** TODO **
    def calculate_year_of_birth(self, _, age):
        return BARI2D_STUDY_START - age  # anonymozation leaves us with no data, use a constant with no effort to estimate

    def get_study_person_ids(self, con): 
        """ Returns distinct person IDs from the dataset in the ohdsi format. """
        cur = con.cursor()
        cur.execute("SELECT distinct id FROM bari2d.\"BARI2D_BL\"")
        ids = map((lambda x: self.convert_person_id_to_ohdsi(x[0])), cur.fetchall()) 
        cur.close()
        return list(ids)

    def convert_person_id_to_ohdsi(self, id) : 
        int_id = int(id[1:])
        return int_id + BARI2D_PERSON_ID_OFFSET 

    def convert_person_id_to_study(self, id) : 
        int_id = id - BARI2D_PERSON_ID_OFFSET
        return "N" + str(int_id)


    # *** TODO *** 
    def populate_person(self, con): # TODO consider this .... is it OK? ...could be part of migrate() driven by to_table/to_column data in study_to_ohdsi_mapping.
        cur = con.cursor()
        # race_cat is 1-3, then race_other is 0 or 1. This makes other a 4th.
        cur.execute("SELECT t.id, t.age, t.sex, t.race  FROM bari2d.\"BARI2D_BL\" t")
        rows = cur.fetchall()
        for row in rows:
            logger.info("PERSON.populate_person() ROW:%s id:%s", row[0], row)
            stmt_string=""
            race=0
            try:
                person_id = self.convert_person_id_to_ohdsi(row[0]) 
                yob =  self.calculate_year_of_birth("", row[1])
                gender_concept_id = sex_to_concept_m1f2(row[2])
                race = bari2d_race_to_concept(row[3])

                stmt_string = ("INSERT INTO person (person_id, gender_concept_id, year_of_birth, race_concept_id, ethnicity_concept_id) " 
                    "VALUES (%s, %s, %s, %s, %s)")
                cur.execute(stmt_string, (person_id, gender_concept_id, yob, race, UNKNOWN_ETHNICITY))
            except Exception as e:
                logger.error("populate_person():%s %s race:%s  %s", row, stmt_string, race, e)
                raise
        cur.close()
        con.commit()
   
    def get_id_field_name(self):
        return "id"
    
    def get_date_column_for_table(self, table_name):
        return "'2010-01-01 00:00:00'" # TODO anonymization leaves us with no data here, using a constant

    def use_date_column_on_select(self):
        return False
