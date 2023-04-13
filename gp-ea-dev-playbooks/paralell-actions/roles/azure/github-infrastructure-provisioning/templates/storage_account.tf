#Create Storage Account
module "storage_account" {
  source = "git::https://github.build.ge.com/gp-azr-core/az-app-infra.git//modules/storage_account?ref=1.1"
  subcode = var.subcode
  region = var.region
  uai = var.uai
  env = var.env
  appName = var.appName
  keyvault_id = module.key_vault.keyvault-id
  keyvault_name = module.key_vault.keyvault-name
  keyvault_rg = module.key_vault.keyvault-rg
  key_name = module.key_vault_key.key-name
  subscription_id = var.subscription_id
  storage_acc_type = "LRS"
  purpose = "{{ storage_account_purpose }}"
  resource_group = "{{ resource_group }}"
}

#Create Storage Account Container
module "storage_account_container" {
  source = "git::https://github.build.ge.com/gp-azr-core/az-app-infra.git//modules/storage_account_container?ref=1.0"
  storage_container_name = "{{ storage_account_container_name }}"
  storage_account_name = module.storage_account.storageaccount-name
  depends_on = [
    module.storage_account
  ]
}

#Create key vault private endpoint
module "storage_account_private_endpoint" {
  source = "git::https://github.build.ge.com/gp-azr-core/az-app-infra.git//modules/storage_account_private_endpoint?ref=1.0"
  subcode = var.subcode
  uai = var.uai
  env = var.env
  appName = var.appName
  region = var.region
  storage_account_id = module.storage_account.storageaccount-id
  storage_account_name = module.storage_account.storageaccount-name
  resource_group = "{{ resource_group }}"

  #Make sure container is created before private endpoint is made
  depends_on = [
    module.storage_account_container
  ]
}