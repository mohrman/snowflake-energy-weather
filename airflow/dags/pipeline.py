import sys
sys.path.insert(0, "/opt/airflow/ingestion/..")

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from ingestion.energy import create_table as energy_create_table, fetch_and_stage as energy_fetch_and_stage, delete_existing as energy_delete_existing, copy_into as energy_copy_into
from ingestion.weather import create_table as weather_create_table, fetch_and_stage as weather_fetch_and_stage, delete_existing as weather_delete_existing, copy_into as weather_copy_into

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="pipeline",
    description="Daily ingestion of weather and energy data, followed by dbt transformation",
    schedule="0 7 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["snowflake", "ingestion", "dbt"],
) as dag:

    # Weather ingestion
    w1 = PythonOperator(task_id="weather_create_table", python_callable=weather_create_table)
    w2 = PythonOperator(task_id="weather_fetch_and_stage", python_callable=weather_fetch_and_stage)
    w3 = PythonOperator(task_id="weather_delete_existing", python_callable=weather_delete_existing)
    w4 = PythonOperator(task_id="weather_copy_into", python_callable=weather_copy_into)

    # Energy ingestion
    e1 = PythonOperator(task_id="energy_create_table", python_callable=energy_create_table)
    e2 = PythonOperator(task_id="energy_fetch_and_stage", python_callable=energy_fetch_and_stage)
    e3 = PythonOperator(task_id="energy_delete_existing", python_callable=energy_delete_existing)
    e4 = PythonOperator(task_id="energy_copy_into", python_callable=energy_copy_into)

    # dbt transformation
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run --profiles-dir /opt/airflow/dbt",
    )

    # Dependencies
    w1 >> w2 >> w3 >> w4
    e1 >> e2 >> e3 >> e4
    [w4, e4] >> dbt_run
