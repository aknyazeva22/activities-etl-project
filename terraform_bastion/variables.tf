variable "allowed_db_cidr" {
  type    = string
  default = "0.0.0.0"
}

variable "db_admin" {
  type    = string
  default = "pgadmin"
}

variable "db_name" {
  type    = string
  default = "postgres"
}

variable "db_password" {
  type    = string
  sensitive = true
}

variable "db_port" {
  type    = string
  default = "5432"
}

variable "host_admin" {
  type    = string
  default = "azureuser"
}

variable "location" {
  type    = string
  default = "France Central"
}

variable "pgdata" {
  type    = string
  default = "/var/lib/postgresql/data/pgdata"
}

variable "postgres_server_name" {
  type    = string
  default = "activities-postgres-server"
}

variable "postgres_version" {
  type    = string
  default = "16"
}

variable "resource_group_name" {
  type    = string
  default = "aa-activities"
}

variable "ssh_public_key_path" {
  type    = string
  default = "~/.ssh/id_rsa.pub"
}

variable "subscription_id" {
  type    = string
  sensitive = true
}

variable "vm_name" {
  type    = string
  default = "pgvm"
}

variable "vnet_cidr" {
  type    = string
  default = "10.50.0.0/16"
}

variable "internal_subnet_cidr" {
  type        = list(string)
  default     = ["10.50.1.0/24"]
}

variable "bastion_subnet_cidr" {
  type        = list(string)
  default     = ["10.50.254.0/24"]
}