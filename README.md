# snowflake-energy-weather

A data platform that ingests weather and energy price data into Snowflake, transforms it with dbt, and visualizes it in a Streamlit app.

## Stack

- **Snowflake** — data warehouse
- **Terraform** — infrastructure as code
- **dbt** — data transformation (staging → mart)
- **Python** — data ingestion (Open-Meteo + ENTSO-E APIs)
- **Streamlit in Snowflake** — dashboard

---

## Infrastructure (Terraform)

All Snowflake resources are managed via Terraform using the `snowflakedb/snowflake` provider.

### Resources provisioned

| Resource | Name |
|---|---|
| Warehouse | `ENERGY_WEATHER_WH` (X-Small, auto-suspend 60s) |
| Databases | `RAW_DB`, `ANALYTICS_DB` |
| Schemas | `RAW_DB.WEATHER`, `RAW_DB.ENERGY`, `ANALYTICS_DB.STAGING`, `ANALYTICS_DB.MART` |
| Roles | `INGESTION_ROLE`, `TRANSFORMER_ROLE`, `REPORTER_ROLE` |

### Setup

```bash
cd terraform

# Create credentials file (gitignored)
cp terraform.tfvars.example terraform.tfvars
# Fill in your Snowflake credentials

terraform init
terraform apply
```
