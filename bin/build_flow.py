

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email': ['chris.roeder@ucdenver.edu'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('harmonization', default_args=default_args)

ohdsi     = BaseOperator(task_id='ohdsi', bash_command='ohdsi.sh', dag=dag)
load      = BaseOperator(task_id='load', bash_command='load.sh', dag=dag)
ohdsi >> load
meta      = BaseOperator(task_id='meta', bash_command='meta.sh', dag=dag)
load >> meta
migrate_calculate   = BaseOperator(task_id='migrate', bash_command='migrate.sh', dag=dag)
migrate_calculate >> load
extract   = BaseOperator(task_id='extract', bash_command='extract.sh', dag=dag)
extract >> migrate_calculate
check     = BaseOperator(task_id='check', bash_command='check.sh', dag=dag)
check >>  #??
analyze   = BaseOperator(task_id='analyze', bash_command='analyze.sh', dag=dag)
analyze >> #??
report    = BaseOperator(task_id='report', bash_command='report.sh', dag=dag)
report >> calculate
test      = BaseOperator(task_id='test', bash_command='test.sh', dag=dag)
test >> calculate
unit_test = BaseOperator(task_id='unit_test', bash_command='utest.sh', dag=dag)


