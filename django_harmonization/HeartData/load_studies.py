
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
 load.py
 Python Version: 3.6.3


    Loads csv files based on entries in the study_files table. 
    Updates the "loaded" column in the study table on success.
  
 Works outside of Django ORM so we can use the CSV reader from Pandas.
'''

import argh
import psycopg2
import re
import logging
import pandas
from sqlalchemy import create_engine
import os

STUDIES_DIR = "/opt/local/harmonization/deployment/studies"

def main(study_name):
    ''' 
        load_studies.py loads studies configured in the study table.
        This is restrcited to reading the csv files and creating tables for them. 
        study_name can be None, or 'ALL', or the specific name of a single study
    ''' 
    
    DBNAME=os.environ.get('PGDATABASE'),
    USERNAME=os.environ.get('PGUSER'),
    PASSWORD=os.environ.get('PGPASSWORD'),
    HOST=os.environ.get('PGHOST'),
    PORT=os.environ.get('PGPORT'),
    logger = logging.getLogger(__name__)
    con = psycopg2.connect(database=DBNAME[0], user=USERNAME[0]) 
    con.autocommit=True;

    stmt=''
    if study_name == None or study_name == 'ALL' or study_name == 'all' or study_name == 'All':
        stmt = 'SELECT study_name, study_id, loaded from study;' 
    else:
        stmt = 'SELECT study_name, study_id, loaded from study where study_name =\'' + study_name + '\';'

    cur = con.cursor()
    try:
        cur.execute(stmt)
        study_rows = cur.fetchall()
    except Exception as  e:
        logger.error("unable to select studies for load: %s, %s",  study_name, e, stmt)
        raise e

    name_re = r'.*/(\w+)\.csv' # capture filename part from path
    for row in study_rows:
        print("STUDY ROW:", row)
        if (row[0] != 'NULL') :
            study_name = row[0]
            study_id = row[1]
            try:
                logger.info("creating schema:\"%s\"", study_name.lower())
                cur.execute('CREATE SCHEMA ' + study_name.lower())
            except Exception as ex:
                logger.error(ex)
                # do notraise ex, it's OK for the schema to already have existed
            stmt = 'SELECT file_path from study_files where study_id = %s'
            cur.execute(stmt, (study_id,))
            file_rows = cur.fetchall()
            all_files=True
            for filepath in file_rows:
                fileMatch = re.match(name_re, filepath[0])
                table_name = fileMatch.group(1)
                filename = STUDIES_DIR + "/" + filepath[0]
                print("loading schema:\"{}\", table:\"{}\" with file:\"{}\" ".format(study_name.lower(), table_name, filename)) # CR
                logger.info("loading schema:\"%s\", table:\"%s\" with file:\"%s\" ", study_name.lower(), table_name, filepath[0]) # CR
                schema_table=study_name.lower() + '.' + table_name
                try:
                    cur.execute("DROP TABLE {}".format(schema_table))
                except Exception as ex:
                    logger.error(ex)
                    ## do not raise ex, it's OK if there is no table before we try to drop it
 
                ENGINE = create_engine('postgresql://'+ USERNAME[0] + ':' + PASSWORD[0] + '@' + HOST[0] + ':' + PORT[0] + '/' + DBNAME[0])
                logger.info(filename)
                try :
                    df = pandas.read_csv(filename)
                    df.columns = [c.lower() for c in df.columns] #postgres doesn't like capitals or spaces
                    df.to_sql(table_name, ENGINE, schema=study_name.lower())
                except Exception as  e:
                    all_files=False

                    logger.error("load_studies file failed file:\"%s\"   table:\"%s\" schema:\"%s\"", 
                        filename, table_name, study_name.lower())
                    logger.error("  exception: %s", e)
##                    raise e

            if (all_files) :
                update_stmt = 'UPDATE study set loaded=\'t\' where study_name=%s'
                update_cur = con.cursor()
                try:
                    logger.warning("load_studies: marking {} as loaded: {}".format(study_name, update_stmt))
                    update_cur.execute(update_stmt, (study_name,) )
                    update_cur.execute("select * from study where study_name=%s", (study_name,))
                    check_rows = update_cur.fetchall()
                    update_cur.close()
                except Exception as  e:
                    logger.error("unable to mark %s as loaded: %s, %s",  study_name, e, update_stmt)
                    raise e

    con.close()
    if (all_files):
        logger.warning("EXTRACT complete")
        return True
    else:
        return False


if __name__ == '__main__':
    # http://argh.readthedocs.io/en/latest/tutorial.html#assembling-commands
    parser = argh.ArghParser()
    argh.set_default_command(parser, main)
    argh.dispatch(parser)
