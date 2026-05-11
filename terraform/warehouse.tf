resource "snowflake_warehouse" "compute" {
  name                = "ENERGY_WEATHER_WH"
  warehouse_size      = "X-SMALL"
  auto_suspend        = 60
  auto_resume         = true
  initially_suspended = true
}

resource "snowflake_grant_privileges_to_account_role" "ingestion_warehouse_usage" {
  account_role_name = snowflake_account_role.ingestion.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.compute.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_warehouse_usage" {
  account_role_name = snowflake_account_role.transformer.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.compute.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "reporter_warehouse_usage" {
  account_role_name = snowflake_account_role.reporter.name
  privileges        = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.compute.name
  }
}
