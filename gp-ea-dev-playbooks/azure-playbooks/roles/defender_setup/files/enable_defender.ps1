Param(
  [String] $subscription_name,
  [String] $subscription_id
)

Connect-AzAccount -Identity -AccountId "ec4d7eec-bf83-465d-a693-8c5e98bd84bd"

Set-AzContext -Subscription $subscription_name
Register-AzResourceProvider -ProviderNamespace 'Microsoft.Security'

$defender_items = "SqlServers","AppServices", "SqlServerVirtualMachines","Containers","VirtualMachines","StorageAccounts","KeyVaults" , "Dns" ,"Arm", "OpenSourceRelationalDatabases","CosmosDbs"
# Older items
#$defender_items = "SqlServers","AppServices", "SqlServerVirtualMachines","Containers","VirtualMachines","StorageAccounts","KeyVaults"
 
foreach ($item in $defender_items)
 {
       Set-AzSecurityPricing -Name $item -PricingTier "Standard"
}

Set-AzSecurityWorkspaceSetting -Name "default" -Scope "/subscriptions/$subscription_id" -WorkspaceId "/subscriptions/9c1ab385-2554-43ca-bdf8-f8d937bf4a28/resourcegroups/cs-loganalytics/providers/microsoft.operationalinsights/workspaces/328-gr-logs"
Set-AzSecurityAutoProvisioningSetting -Name "default" -EnableAutoProvision
