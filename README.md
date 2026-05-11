# snowflake-energy-weather

## Stack

- **Snowflake** — data warehouse
- **Terraform** — infrastructure as code
- **Airflow** — orchestration (local Docker Compose)
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
cp terraform.tfvars.example terraform.tfvars  # fill in your Snowflake credentials
terraform init
terraform apply
```

---

## Orchestration (Airflow)

DAGs are scheduled using Apache Airflow 2, running locally via Docker Compose.

### Start

1. `cp airflow/.env.example airflow/.env` and fill in your credentials
2. `cd airflow && docker compose up airflow-init` — initialises the database (first time only)
3. `docker compose up -d` — starts the scheduler and webserver
4. Open http://localhost:8081 — login with `admin` / `admin`

### Stop

```bash
cd airflow && docker compose down
```
