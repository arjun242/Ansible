#Create key vault
module "{{ module }}" {
  source = "git::https://github.build.ge.com/gp-azr-core/az-app-infra.git//modules/key_vault?ref=1.0"
  subcode = var.subcode
  region = var.region 
  uai = var.uai 
  env = var.env
  appName = var.appName
  subscription_id = var.subscription_id
  purpose = "{{contents.purpose}}"
  resource_group = "{{contents.resource_group}}"
}