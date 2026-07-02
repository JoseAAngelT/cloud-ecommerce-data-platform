variable "project_name" {
  description = "Project name used for Azure resource naming."
  type        = string
  default     = "ecommerce"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region where resources will be created."
  type        = string
  default     = "eastus"
}

variable "sql_admin_username" {
  description = "Azure SQL administrator username."
  type        = string
  default     = "sqladminuser"
}

variable "sql_admin_password" {
  description = "Azure SQL administrator password."
  type        = string
  sensitive   = true
}

variable "unique_suffix" {
  description = "Unique suffix used for globally unique Azure resource names."
  type        = string
  default     = "jta01"
}

variable "enable_sql" {
  description = "Whether to create Azure SQL resources."
  type        = bool
  default     = false
}