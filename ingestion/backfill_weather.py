"""
Backfill historical weather data using Open-Meteo archive API.
Run from the project root:
    set -a && source .env && set +a
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m ingestion.backfill_weather
"""
import time
from datetime import date, timedelta
import requests
from ingestion.utils import get_connection
from ingestion.weather import CITIES

START_DATE = date(2026, 1, 1)
END_DATE = date.today() - timedelta(days=1)


def fetch_city(city: dict) -> list[tuple]:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max,weather_code",
        "start_date": START_DATE.isoformat(),
        "end_date": END_DATE.isoformat(),
        "timezone": "Europe/Stockholm",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()["daily"]

    rows = []
    for i, d in enumerate(data["time"]):
        rows.append((
            city["name"], city["bidding_zone"], city["lat"], city["lon"], d,
            data["temperature_2m_max"][i],
            data["temperature_2m_min"][i],
            data["temperature_2m_mean"][i],
            data["precipitation_sum"][i],
            data["wind_speed_10m_max"][i],
            data["weather_code"][i],
        ))
    return rows


if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM RAW_DB.WEATHER.DAILY_WEATHER WHERE date >= %s AND date <= %s",
                (START_DATE.isoformat(), END_DATE.isoformat()))
    print(f"Cleared existing weather data from {START_DATE} to {END_DATE}")

    total = 0
    for city in CITIES:
        print(f"Fetching {city['name']}...")
        rows = fetch_city(city)
        cur.executemany("""
            INSERT INTO RAW_DB.WEATHER.DAILY_WEATHER
                (city, bidding_zone, latitude, longitude, date,
                 temp_max, temp_min, temp_mean, precipitation, wind_speed_max, weather_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, rows)
        total += len(rows)
        print(f"  Inserted {len(rows)} rows")
        time.sleep(0.5)

    conn.commit()
    conn.close()
    print(f"\nDone. Inserted {total} weather rows total.")
