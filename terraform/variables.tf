variable "snowflake_organization_name" {
  description = "Snowflake organization name (e.g. TAFYYZJ)"
  type        = string
}

variable "snowflake_account_name" {
  description = "Snowflake account name (e.g. WI45960)"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake user for Terraform"
  type        = string
}

variable "snowflake_password" {
  description = "Snowflake password for Terraform user"
  type        = string
  sensitive   = true
}
