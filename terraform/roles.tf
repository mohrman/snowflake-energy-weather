resource "snowflake_account_role" "ingestion" {
  name    = "INGESTION_ROLE"
  comment = "Write access to RAW_DB only"
}

resource "snowflake_account_role" "transformer" {
  name    = "TRANSFORMER_ROLE"
  comment = "Read RAW_DB, write ANALYTICS_DB (dbt)"
}

resource "snowflake_account_role" "reporter" {
  name    = "REPORTER_ROLE"
  comment = "Read-only on ANALYTICS_DB (Streamlit)"
}
