output "postgres_server" {
  value = azurerm_postgresql_flexible_server.main.name
}

output "db_host" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "db_user" {
  value = var.db_admin
}

output "db_password" {
  value = var.db_password
  sensitive = true
}

output "db_name" {
  value = "postgres"
}
