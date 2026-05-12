resource "snowflake_database" "raw" {
  name    = "RAW_DB"
  comment = "Landing zone for raw API data"
}

resource "snowflake_database" "analytics" {
  name    = "ANALYTICS_DB"
  comment = "dbt staging and mart models"
}

resource "snowflake_grant_privileges_to_account_role" "ingestion_raw_usage" {
  account_role_name = snowflake_account_role.ingestion.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.raw.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_raw_usage" {
  account_role_name = snowflake_account_role.transformer.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.raw.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_analytics_usage" {
  account_role_name = snowflake_account_role.transformer.name
  privileges        = ["USAGE", "CREATE SCHEMA"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.analytics.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "reporter_analytics_usage" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.analytics.name
  }
}
