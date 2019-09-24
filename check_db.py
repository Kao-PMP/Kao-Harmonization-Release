#!/usr/bin/env python3

import psycopg2
import logging 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#con = psycopg2.connect(database='postgres', user='postgres') 
con = psycopg2.connect(database='heart_db_v3', user='christopherroeder') 
cur = con.cursor()
cur.execute("select distinct table_name from information_schema.columns")
rows = cur.fetchall()
print(rows)
cur.close()
con.close()
