#####################
# NSG allowing 22 and 5435
#####################
resource "azurerm_network_security_group" "nsg" {
  name                = "nsg-pgvm"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.allowed_db_cidr  # lock down SSH as well
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "postgres"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = var.db_port
    source_address_prefix      = var.allowed_db_cidr
    destination_address_prefix = "*"
  }
}

#####################
# NIC (+ optional Public IP)
#####################
# If you don’t want a public IP, comment this out and the 'public_ip_address_id' on NIC.
resource "azurerm_public_ip" "pip" {
  name                = "pip-pgvm"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  domain_name_label   = var.postgres_server_name
}

resource "azurerm_network_interface" "nic" {
  name                = "nic-pgvm"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "ipcfg"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.pip.id  # remove if private-only
  }
}

resource "azurerm_network_interface_security_group_association" "nic_nsg" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}