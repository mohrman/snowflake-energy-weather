resource "snowflake_schema" "streamlit" {
  database = snowflake_database.analytics.name
  name     = "STREAMLIT"
}

resource "snowflake_stage" "streamlit" {
  database = snowflake_database.analytics.name
  schema   = snowflake_schema.streamlit.name
  name     = "STREAMLIT_STAGE"
  comment  = "Holds Streamlit app source files"
}

resource "snowflake_streamlit" "app" {
  database          = snowflake_database.analytics.name
  schema            = snowflake_schema.streamlit.name
  name              = "ENERGY_WEATHER_APP"
  stage             = "${snowflake_database.analytics.name}.${snowflake_schema.streamlit.name}.${snowflake_stage.streamlit.name}"
  main_file         = "app.py"
  query_warehouse   = snowflake_warehouse.compute.name
  comment           = "Weather vs energy price explorer"
}

resource "snowflake_grant_privileges_to_account_role" "reporter_streamlit_schema" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.analytics.name}\".\"${snowflake_schema.streamlit.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "reporter_streamlit_usage" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["USAGE"]
  on_schema_object {
    object_type = "STREAMLIT"
    object_name = "${snowflake_database.analytics.name}.${snowflake_schema.streamlit.name}.${snowflake_streamlit.app.name}"
  }
}
