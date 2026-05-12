{{ config(database='ANALYTICS_DB', schema='STAGING') }}

with source as (
    select * from RAW_DB.WEATHER.DAILY_WEATHER
),

renamed as (
    select
        city,
        bidding_zone,
        latitude,
        longitude,
        date                            as weather_date,
        temp_max                        as temperature_max_c,
        temp_min                        as temperature_min_c,
        temp_mean                       as temperature_mean_c,
        precipitation                   as precipitation_mm,
        wind_speed_max                  as wind_speed_max_kmh,
        weather_code,
        ingested_at
    from source
)

select * from renamed
