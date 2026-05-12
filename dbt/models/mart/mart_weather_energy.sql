{{ config(database='ANALYTICS_DB', schema='MART') }}

with weather as (
    select * from {{ ref('stg_weather') }}
),

energy_daily as (
    select
        bidding_zone,
        price_date,
        avg(price_eur_mwh)              as price_avg_eur_mwh,
        min(price_eur_mwh)              as price_min_eur_mwh,
        max(price_eur_mwh)              as price_max_eur_mwh
    from {{ ref('stg_energy') }}
    group by bidding_zone, price_date
),

joined as (
    select
        w.weather_date                  as date,
        w.city,
        w.bidding_zone,
        w.latitude,
        w.longitude,
        w.temperature_max_c,
        w.temperature_min_c,
        w.temperature_mean_c,
        w.precipitation_mm,
        w.wind_speed_max_kmh,
        w.weather_code,
        e.price_avg_eur_mwh,
        e.price_min_eur_mwh,
        e.price_max_eur_mwh
    from weather w
    left join energy_daily e
        on w.bidding_zone = e.bidding_zone
        and w.weather_date = e.price_date
)

select * from joined
