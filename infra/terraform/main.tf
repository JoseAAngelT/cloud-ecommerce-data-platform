locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.name_prefix}"
  location = var.location
}

resource "azurerm_storage_account" "datalake" {
  name                     = replace("st${var.project_name}${var.environment}", "-", "")
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
  name                         = "sql-${local.name_prefix}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
}

resource "azurerm_mssql_database" "main" {
  name      = "sqldb-${local.name_prefix}"
  server_id = azurerm_mssql_server.main.id
  sku_name  = "Basic"
}

resource "azurerm_data_factory" "main" {
  name                = "adf-${local.name_prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}