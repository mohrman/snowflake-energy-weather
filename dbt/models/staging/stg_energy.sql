{{ config(database='ANALYTICS_DB', schema='STAGING') }}

with source as (
    select * from RAW_DB.ENERGY.HOURLY_PRICES
),

renamed as (
    select
        bidding_zone,
        timestamp_utc,
        date(timestamp_utc)             as price_date,
        hour(timestamp_utc)             as price_hour,
        price_eur_mwh,
        ingested_at
    from source
)

select * from renamed
