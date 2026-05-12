import os
import snowflake.connector


def get_connection(role: str = "INGESTION_ROLE"):
    return snowflake.connector.connect(
        account=f"{os.environ['SNOWFLAKE_ORGANIZATION_NAME']}-{os.environ['SNOWFLAKE_ACCOUNT_NAME']}",
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse="ENERGY_WEATHER_WH",
        role=role,
    )


def make_create_table_task(setup_sql: list[str]):
    def create_table(**context):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                for sql in setup_sql:
                    cur.execute(sql)
        finally:
            conn.close()
    return create_table


def make_delete_existing_task(delete_sql: str, date_field: str):
    def delete_existing(**context):
        target_date = context["data_interval_start"].date()
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(delete_sql.format(target_date=target_date))
                print(f"Deleted existing rows for {target_date}")
        finally:
            conn.close()
    return delete_existing


def make_copy_into_task(copy_sql: str):
    def copy_into(**context):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(copy_sql)
                print("COPY INTO complete")
        finally:
            conn.close()
    return copy_into
