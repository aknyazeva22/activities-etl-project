#####################
# Outputs
#####################
output "db_server" {
  value = azurerm_public_ip.pip.fqdn
  description = "Hostname for PostgreSQL connection"
}

output "db_host" {
  value = azurerm_public_ip.pip.ip_address
  description = "Host IP for PostgreSQL connection"
}

output "db_port" {
  value = var.db_port
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

output "postgres_example_conn_str" {
  value       = "postgresql://${var.db_admin}:${var.db_password}@${azurerm_public_ip.pip.ip_address}:${var.db_port}/${var.db_name}"
  description = "Connection string"
  sensitive   = true
}