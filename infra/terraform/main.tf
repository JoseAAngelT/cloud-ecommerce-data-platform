locals {
  name_prefix          = "${var.project_name}-${var.environment}-${var.unique_suffix}"
  storage_account_name = lower(replace("st${var.project_name}${var.environment}${var.unique_suffix}", "-", ""))
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.name_prefix}"
  location = var.location
}

resource "azurerm_storage_account" "datalake" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  is_hns_enabled = true
}

resource "azurerm_storage_container" "landing" {
  name                  = "landing"
  storage_account_id    = azurerm_storage_account.datalake.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_id    = azurerm_storage_account.datalake.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_id    = azurerm_storage_account.datalake.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_id    = azurerm_storage_account.datalake.id
  container_access_type = "private"
}

resource "azurerm_key_vault" "main" {
  name                = "kv-${local.name_prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
}

data "azurerm_client_config" "current" {}

resource "azurerm_mssql_server" "main" {
  count = var.enable_sql ? 1 : 0

  name                         = "sql-${local.name_prefix}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
}

resource "azurerm_mssql_database" "main" {
  count = var.enable_sql ? 1 : 0

  name      = "sqldb-${local.name_prefix}"
  server_id = azurerm_mssql_server.main[0].id
  sku_name  = "Basic"
}

resource "azurerm_data_factory" "main" {
  name                = "adf-${local.name_prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "adf_storage_blob_contributor" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.main.identity[0].principal_id
}