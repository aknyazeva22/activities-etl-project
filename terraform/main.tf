provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
  use_cli = true
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = var.postgres_server_name
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  administrator_login    = var.db_admin
  administrator_password = var.db_password
  version                = "13"
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  zone                   = "1"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_all" {
  name             = "AllowAll"
  server_id	   = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

output "postgres_connection_string" {
  value = "postgresql://${var.db_admin}:${var.db_password}@${azurerm_postgresql_flexible_server.main.name}.postgres.database.azure.com:5432/postgres"
  sensitive = true
}
