#####################
# Outputs
#####################
output "db_server" {
  value = azurerm_public_ip.bastion_pip.fqdn
  description = "Hostname for PostgreSQL connection"
}

output "db_host" {
  value = "127.0.0.1"
  description = "Host IP for PostgreSQL connection (local)"
}

output "bastion_host" {
  value = azurerm_public_ip.bastion_pip.ip_address
  description = "Host IP for Bastion connection"
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
  value       = "postgresql://${var.db_admin}:${var.db_password}@127.0.0.1:${var.db_port}/${var.db_name}"
  description = "Connection string"
  sensitive   = true
}
