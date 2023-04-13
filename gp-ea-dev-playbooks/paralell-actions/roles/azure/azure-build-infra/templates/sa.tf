#Create Storage Account
module "{{ module }}" {
  source = "git::https://github.build.ge.com/gp-azr-core/az-app-infra.git//modules/storage_account?ref=1.0"
  subcode = var.subcode
  region = var.region 
  uai = var.uai 
  env = var.env
  appName = var.appName
  keyvault_id = module.{{contents.key_vault}}.keyvault-id
  keyvault_name = module.{{contents.key_vault}}.keyvault-name
  keyvault_rg = module.{{contents.key_vault}}.keyvault-rg
  key_name = module.{{contents.key_vault_key}}.key-name
  subscription_id = var.subscription_id
  storage_acc_type = "{{contents.storage_account_type}}"
  purpose = "{{contents.storage_account_purpose}}"
  resource_group = "{{contents.resource_group}}"
}