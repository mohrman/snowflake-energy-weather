"""
One-off script to seed historical weather and energy data from 2026-01-01 to yesterday.
Run from the project root:
    set -a && source .env && set +a
    python -m ingestion.seed_historical
"""
import random
import math
from datetime import date, timedelta
from ingestion.utils import get_connection
from ingestion.weather import CITIES

random.seed(42)

START_DATE = date(2026, 1, 1)
END_DATE = date.today() - timedelta(days=1)

BIDDING_ZONES = ["SE1", "SE2", "SE3", "SE4"]


def day_of_year_temperature(d: date, lat: float) -> float:
    """Seasonal mean temperature based on day of year and latitude."""
    doy = d.timetuple().tm_yday
    # Coldest around day 15 (Jan 15), warmest around day 197 (Jul 16)
    seasonal = -math.cos(2 * math.pi * (doy - 15) / 365)
    # Higher latitude = colder
    base = 8 - (lat - 55) * 0.6
    return base + seasonal * 12


def generate_weather_rows():
    rows = []
    d = START_DATE
    while d <= END_DATE:
        for city in CITIES:
            mean = day_of_year_temperature(d, city["lat"]) + random.gauss(0, 2)
            spread = random.uniform(4, 10)
            temp_max = mean + spread / 2
            temp_min = mean - spread / 2
            precipitation = max(0, random.gauss(1.5, 2.5))
            wind_speed = max(0, random.gauss(18, 8))
            weather_code = random.choice([0, 1, 2, 3, 61, 71, 80])
            rows.append((
                city["name"], city["bidding_zone"],
                city["lat"], city["lon"],
                d.isoformat(),
                round(temp_max, 1), round(temp_min, 1), round(mean, 1),
                round(precipitation, 1), round(wind_speed, 1),
                weather_code,
            ))
        d += timedelta(days=1)
    return rows


def generate_energy_rows():
    rows = []
    d = START_DATE
    while d <= END_DATE:
        # Base price per zone, with seasonal component (higher in winter)
        doy = d.timetuple().tm_yday
        seasonal_factor = 1 + 0.4 * (-math.cos(2 * math.pi * (doy - 15) / 365))
        zone_base = {"SE1": 55, "SE2": 60, "SE3": 65, "SE4": 70}

        for zone in BIDDING_ZONES:
            daily_base = zone_base[zone] * seasonal_factor + random.gauss(0, 8)
            for hour in range(24):
                # Higher prices morning (7-9) and evening (17-20)
                if 7 <= hour <= 9 or 17 <= hour <= 20:
                    hour_factor = 1.2
                elif 0 <= hour <= 5:
                    hour_factor = 0.7
                else:
                    hour_factor = 1.0
                price = max(0, daily_base * hour_factor + random.gauss(0, 5))
                ts = f"{d.isoformat()} {hour:02d}:00:00"
                rows.append((zone, ts, round(price, 2)))
        d += timedelta(days=1)
    return rows


def load_weather(conn, rows):
    cur = conn.cursor()
    cur.execute("DELETE FROM RAW_DB.WEATHER.DAILY_WEATHER WHERE date >= %s AND date <= %s",
                (START_DATE.isoformat(), END_DATE.isoformat()))
    cur.executemany("""
        INSERT INTO RAW_DB.WEATHER.DAILY_WEATHER
            (city, bidding_zone, latitude, longitude, date,
             temp_max, temp_min, temp_mean, precipitation, wind_speed_max, weather_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, rows)
    print(f"Inserted {len(rows)} weather rows")


def load_energy(conn, rows):
    cur = conn.cursor()
    cur.execute("DELETE FROM RAW_DB.ENERGY.HOURLY_PRICES WHERE DATE(timestamp_utc) >= %s AND DATE(timestamp_utc) <= %s",
                (START_DATE.isoformat(), END_DATE.isoformat()))
    cur.executemany("""
        INSERT INTO RAW_DB.ENERGY.HOURLY_PRICES (bidding_zone, timestamp_utc, price_eur_mwh)
        VALUES (%s, %s, %s)
    """, rows)
    print(f"Inserted {len(rows)} energy rows")


if __name__ == "__main__":
    print(f"Seeding data from {START_DATE} to {END_DATE}...")
    weather_rows = generate_weather_rows()
    energy_rows = generate_energy_rows()

    conn = get_connection()
    try:
        load_weather(conn, weather_rows)
        load_energy(conn, energy_rows)
        conn.commit()
    finally:
        conn.close()

    print("Done.")
