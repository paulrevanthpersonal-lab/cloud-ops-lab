output "resource_group_name" {
  value = azurerm_resource_group.lab.name
}

output "workspace_id" {
  value = azurerm_log_analytics_workspace.lab.id
}
