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

resource "snowflake_grant_account_role" "ingestion_to_user" {
  role_name = snowflake_account_role.ingestion.name
  user_name = var.snowflake_username
}

resource "snowflake_grant_account_role" "transformer_to_user" {
  role_name = snowflake_account_role.transformer.name
  user_name = var.snowflake_username
}

resource "snowflake_grant_account_role" "reporter_to_user" {
  role_name = snowflake_account_role.reporter.name
  user_name = var.snowflake_username
}
