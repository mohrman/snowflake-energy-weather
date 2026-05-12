import sys
sys.path.insert(0, "/opt/airflow/ingestion/..")

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from ingestion.energy import create_table, fetch_and_stage, delete_existing, copy_into

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="energy_ingestion",
    description="Daily ingestion of SE1-SE4 electricity spot prices into Snowflake",
    schedule="0 8 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["snowflake", "energy"],
) as dag:

    t1 = PythonOperator(task_id="create_table", python_callable=create_table)
    t2 = PythonOperator(task_id="fetch_and_stage", python_callable=fetch_and_stage)
    t3 = PythonOperator(task_id="delete_existing", python_callable=delete_existing)
    t4 = PythonOperator(task_id="copy_into", python_callable=copy_into)

    t1 >> t2 >> t3 >> t4
