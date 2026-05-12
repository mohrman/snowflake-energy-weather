resource "snowflake_schema" "raw_weather" {
  database = snowflake_database.raw.name
  name     = "WEATHER"
}

resource "snowflake_schema" "raw_energy" {
  database = snowflake_database.raw.name
  name     = "ENERGY"
}

resource "snowflake_schema" "staging" {
  database = snowflake_database.analytics.name
  name     = "STAGING"
}

resource "snowflake_schema" "mart" {
  database = snowflake_database.analytics.name
  name     = "MART"
}

# INGESTION_ROLE — access to raw schemas
resource "snowflake_grant_privileges_to_account_role" "ingestion_weather_usage" {
  account_role_name = snowflake_account_role.ingestion.name
  privileges        = ["USAGE", "CREATE TABLE", "CREATE STAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.raw.name}\".\"${snowflake_schema.raw_weather.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "ingestion_energy_usage" {
  account_role_name = snowflake_account_role.ingestion.name
  privileges        = ["USAGE", "CREATE TABLE", "CREATE STAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.raw.name}\".\"${snowflake_schema.raw_energy.name}\""
  }
}

# TRANSFORMER_ROLE — read raw, write analytics
resource "snowflake_grant_privileges_to_account_role" "transformer_raw_weather_usage" {
  account_role_name = snowflake_account_role.transformer.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.raw.name}\".\"${snowflake_schema.raw_weather.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_raw_energy_usage" {
  account_role_name = snowflake_account_role.transformer.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.raw.name}\".\"${snowflake_schema.raw_energy.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_staging_usage" {
  account_role_name = snowflake_account_role.transformer.name
  privileges        = ["USAGE", "CREATE TABLE", "CREATE VIEW"]
  on_schema {
    schema_name = "\"${snowflake_database.analytics.name}\".\"${snowflake_schema.staging.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_mart_usage" {
  account_role_name = snowflake_account_role.transformer.name
  privileges        = ["USAGE", "CREATE TABLE", "CREATE VIEW"]
  on_schema {
    schema_name = "\"${snowflake_database.analytics.name}\".\"${snowflake_schema.mart.name}\""
  }
}

# REPORTER_ROLE — read-only on analytics
resource "snowflake_grant_privileges_to_account_role" "reporter_staging_usage" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.analytics.name}\".\"${snowflake_schema.staging.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "reporter_mart_usage" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.analytics.name}\".\"${snowflake_schema.mart.name}\""
  }
}

# REPORTER_ROLE — SELECT on all tables in all analytics schemas (includes dbt-created schemas)
resource "snowflake_grant_privileges_to_account_role" "reporter_analytics_select" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["SELECT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_database        = snowflake_database.analytics.name
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "reporter_analytics_select_future" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["SELECT"]
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_database        = snowflake_database.analytics.name
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "reporter_analytics_schemas_usage" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["USAGE"]
  on_schema {
    all_schemas_in_database = snowflake_database.analytics.name
  }
}

# ACCOUNTADMIN — SELECT on analytics tables so Streamlit app (owned by ACCOUNTADMIN) can query them
resource "snowflake_grant_privileges_to_account_role" "accountadmin_analytics_select" {
  account_role_name = "ACCOUNTADMIN"
  privileges        = ["SELECT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_database        = snowflake_database.analytics.name
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "accountadmin_analytics_select_future" {
  account_role_name = "ACCOUNTADMIN"
  privileges        = ["SELECT"]
  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_database        = snowflake_database.analytics.name
    }
  }
}
