import csv
import tempfile
import os
from nordpool import elspot
from ingestion.utils import get_connection, make_create_table_task, make_delete_existing_task, make_copy_into_task

AREAS = ["SE1", "SE2", "SE3", "SE4"]

SETUP_SQL = [
    """
    CREATE TABLE IF NOT EXISTS RAW_DB.ENERGY.HOURLY_PRICES (
        bidding_zone    VARCHAR,
        timestamp_utc   TIMESTAMP_NTZ,
        price_eur_mwh   FLOAT,
        ingested_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )
    """,
    "CREATE STAGE IF NOT EXISTS RAW_DB.ENERGY.ENERGY_STAGE",
]

DELETE_SQL = "DELETE FROM RAW_DB.ENERGY.HOURLY_PRICES WHERE DATE(timestamp_utc) = '{target_date}'"

COPY_SQL = """
COPY INTO RAW_DB.ENERGY.HOURLY_PRICES (bidding_zone, timestamp_utc, price_eur_mwh)
FROM @RAW_DB.ENERGY.ENERGY_STAGE
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 EMPTY_FIELD_AS_NULL = TRUE)
PURGE = TRUE
"""

create_table = make_create_table_task(SETUP_SQL)
delete_existing = make_delete_existing_task(DELETE_SQL, date_field="timestamp_utc")
copy_into = make_copy_into_task(COPY_SQL)


def fetch_and_stage(**context):
    target_date = context["data_interval_start"].date()
    prices = elspot.Prices(currency="EUR")
    data = prices.hourly(end_date=target_date, areas=AREAS)

    rows = []
    for area in AREAS:
        for entry in data["areas"][area]["values"]:
            if entry["value"] is not None:
                rows.append((
                    area,
                    entry["start"].replace(tzinfo=None).isoformat(),
                    float(entry["value"]),
                ))

    with tempfile.NamedTemporaryFile(mode="w", suffix=f"_{target_date}.csv", delete=False, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["bidding_zone", "timestamp_utc", "price_eur_mwh"])
        writer.writerows(rows)
        tmp_path = f.name

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"PUT file://{tmp_path} @RAW_DB.ENERGY.ENERGY_STAGE AUTO_COMPRESS=TRUE")
    finally:
        conn.close()
        os.unlink(tmp_path)

    print(f"Staged {len(rows)} rows for {target_date}")
