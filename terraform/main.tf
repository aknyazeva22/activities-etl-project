#####################
# Resource group and network
#####################

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
  use_cli = true
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-pgvm-basic"
  address_space       = [var.vnet_cidr]
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "snet-pgvm-basic"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_cidr]
}

#####################
# Cloud-init: install & configure Postgres
#####################
locals {
  cloud_init_rendered = templatefile("${path.module}/cloud-init-postgres.yml", {
    ADMIN_USERNAME = var.host_admin
    DB_USER        = var.db_admin
    DB_PASSWORD    = var.db_password
    DB_NAME        = var.db_name
    DB_PORT        = var.db_port
  })
}

#####################
# VM
#####################
data "local_file" "sshkey" { filename = var.ssh_public_key_path }

resource "azurerm_linux_virtual_machine" "vm" {
  name                = var.vm_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  network_interface_ids = [azurerm_network_interface.nic.id]
  size                = "Standard_B2s"

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  admin_username = var.host_admin

  admin_ssh_key {
    username   = var.host_admin
    public_key = data.local_file.sshkey.content
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  # cloud-init
  custom_data = base64encode(local.cloud_init_rendered)
}
