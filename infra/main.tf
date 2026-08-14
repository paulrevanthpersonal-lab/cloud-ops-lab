terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "lab" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_log_analytics_workspace" "lab" {
  name                = "${var.prefix}-logs"
  location            = azurerm_resource_group.lab.location
  resource_group_name = azurerm_resource_group.lab.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

resource "azurerm_monitor_action_group" "operations" {
  name                = "${var.prefix}-operations"
  resource_group_name = azurerm_resource_group.lab.name
  short_name          = "ops-lab"
  tags                = local.common_tags
}

locals {
  common_tags = {
    environment = "lab"
    owner       = var.owner
    managed_by  = "terraform"
    cost_center = "portfolio"
  }
}
