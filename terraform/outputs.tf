output "warehouse_name" {
  description = "Name of the compute warehouse"
  value       = snowflake_warehouse.compute.name
}

output "raw_db_name" {
  description = "Name of the raw database"
  value       = snowflake_database.raw.name
}

output "analytics_db_name" {
  description = "Name of the analytics database"
  value       = snowflake_database.analytics.name
}
