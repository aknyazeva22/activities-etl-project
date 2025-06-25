variable "resource_group_name" {
  type    = string
  default = "aa-activities"
}

variable "location" {
  type    = string
  default = "France Central"
}

variable "postgres_server_name" {
  type    = string
  default = "activities-postgres-server"
}

variable "db_admin" {
  type    = string
  default = "pgadmin"
}

variable "db_password" {
  type    = string
  sensitive = true
}

variable "subscription_id" {
  type    = string
  sensitive = true
}

