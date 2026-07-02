output "resource_group_name" {
  description = "Resource group name."
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "Data Lake storage account name."
  value       = azurerm_storage_account.datalake.name
}

output "key_vault_name" {
  description = "Key Vault name."
  value       = azurerm_key_vault.main.name
}

output "sql_server_name" {
  description = "Azure SQL Server name."
  value       = var.enable_sql ? azurerm_mssql_server.main[0].name : null
}

output "sql_database_name" {
  description = "Azure SQL Database name."
  value       = var.enable_sql ? azurerm_mssql_database.main[0].name : null
}

output "data_factory_name" {
  description = "Azure Data Factory name."
  value       = azurerm_data_factory.main.name
}