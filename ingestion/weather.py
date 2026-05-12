import csv
import tempfile
import os
from datetime import date
import requests
from ingestion.utils import get_connection, make_create_table_task, make_delete_existing_task, make_copy_into_task

CITIES = [
    {"name": "Stockholm",   "lat": 59.3293, "lon": 18.0686, "bidding_zone": "SE3"},
    {"name": "Gothenburg",  "lat": 57.7089, "lon": 11.9746, "bidding_zone": "SE3"},
    {"name": "Malmö",       "lat": 55.6050, "lon": 13.0038, "bidding_zone": "SE4"},
    {"name": "Uppsala",     "lat": 59.8586, "lon": 17.6389, "bidding_zone": "SE3"},
    {"name": "Västerås",    "lat": 59.6099, "lon": 16.5448, "bidding_zone": "SE3"},
    {"name": "Örebro",      "lat": 59.2753, "lon": 15.2134, "bidding_zone": "SE3"},
    {"name": "Linköping",   "lat": 58.4108, "lon": 15.6214, "bidding_zone": "SE3"},
    {"name": "Helsingborg", "lat": 56.0465, "lon": 12.6945, "bidding_zone": "SE4"},
    {"name": "Jönköping",   "lat": 57.7826, "lon": 14.1618, "bidding_zone": "SE2"},
    {"name": "Norrköping",  "lat": 58.5877, "lon": 16.1924, "bidding_zone": "SE3"},
    {"name": "Lund",        "lat": 55.7047, "lon": 13.1910, "bidding_zone": "SE4"},
    {"name": "Umeå",        "lat": 63.8258, "lon": 20.2630, "bidding_zone": "SE2"},
    {"name": "Gävle",       "lat": 60.6749, "lon": 17.1413, "bidding_zone": "SE2"},
    {"name": "Borås",       "lat": 57.7210, "lon": 12.9401, "bidding_zone": "SE3"},
    {"name": "Södertälje",  "lat": 59.1955, "lon": 17.6253, "bidding_zone": "SE3"},
    {"name": "Eskilstuna",  "lat": 59.3666, "lon": 16.5077, "bidding_zone": "SE3"},
    {"name": "Halmstad",    "lat": 56.6745, "lon": 12.8578, "bidding_zone": "SE3"},
    {"name": "Växjö",       "lat": 56.8777, "lon": 14.8091, "bidding_zone": "SE4"},
    {"name": "Sundsvall",   "lat": 62.3913, "lon": 17.3069, "bidding_zone": "SE2"},
    {"name": "Luleå",       "lat": 65.5848, "lon": 22.1547, "bidding_zone": "SE1"},
]

SETUP_SQL = [
    """
    CREATE TABLE IF NOT EXISTS RAW_DB.WEATHER.DAILY_WEATHER (
        city            VARCHAR,
        bidding_zone    VARCHAR,
        latitude        FLOAT,
        longitude       FLOAT,
        date            DATE,
        temp_max        FLOAT,
        temp_min        FLOAT,
        temp_mean       FLOAT,
        precipitation   FLOAT,
        wind_speed_max  FLOAT,
        weather_code    INTEGER,
        ingested_at     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )
    """,
    "CREATE STAGE IF NOT EXISTS RAW_DB.WEATHER.WEATHER_STAGE",
]

DELETE_SQL = "DELETE FROM RAW_DB.WEATHER.DAILY_WEATHER WHERE date = '{target_date}'"

COPY_SQL = """
COPY INTO RAW_DB.WEATHER.DAILY_WEATHER
    (city, bidding_zone, latitude, longitude, date,
     temp_max, temp_min, temp_mean, precipitation, wind_speed_max, weather_code)
FROM @RAW_DB.WEATHER.WEATHER_STAGE
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1 EMPTY_FIELD_AS_NULL = TRUE)
PURGE = TRUE
"""

create_table = make_create_table_task(SETUP_SQL)
delete_existing = make_delete_existing_task(DELETE_SQL, date_field="date")
copy_into = make_copy_into_task(COPY_SQL)


def _fetch_city(city: dict, target_date: date) -> tuple:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max,weather_code",
        "start_date": target_date.isoformat(),
        "end_date": target_date.isoformat(),
        "timezone": "Europe/Stockholm",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()["daily"]
    return (
        city["name"], city["bidding_zone"], city["lat"], city["lon"],
        data["time"][0],
        data["temperature_2m_max"][0], data["temperature_2m_min"][0], data["temperature_2m_mean"][0],
        data["precipitation_sum"][0], data["wind_speed_10m_max"][0], data["weather_code"][0],
    )


def fetch_and_stage(**context):
    target_date = context["data_interval_start"].date()
    rows = [_fetch_city(city, target_date) for city in CITIES]

    with tempfile.NamedTemporaryFile(mode="w", suffix=f"_{target_date}.csv", delete=False, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["city", "bidding_zone", "latitude", "longitude", "date",
                         "temp_max", "temp_min", "temp_mean", "precipitation",
                         "wind_speed_max", "weather_code"])
        writer.writerows(rows)
        tmp_path = f.name

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"PUT file://{tmp_path} @RAW_DB.WEATHER.WEATHER_STAGE AUTO_COMPRESS=TRUE")
    finally:
        conn.close()
        os.unlink(tmp_path)

    print(f"Staged {len(rows)} rows for {target_date}")
