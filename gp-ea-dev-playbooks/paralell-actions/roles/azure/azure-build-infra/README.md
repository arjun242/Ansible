*Module is still under development by EA Team*
# Usage Examples
**Key Vault:**
```yaml
contents:
  purpose: poc
  resource_group: rg-327-uai3047228-ansible-refactor
module: kv-327-uai3047228-poc
org: 327-gp-azr-ops-dev
repo: uai3047228-ansible
resource: key_vault
```

**Storage Account Example:** 
```yaml
contents: 
  key_vault: kv-327-uai3026350-mikesmith-test 
  key_vault_key: key-327-uai3026350-mikesmith-test 
  resource_group: rg-327-uai3026350-mikesmithtest
  storage_account_purpose: archive
  storage_account_type: LRS
module: sa327uai3026350archive 
org: 327-gp-azr-ops-dev 
repo: uai3026350-mikesmithtest 
resource: storage_account 
```

**Linux VM: **
```yaml
contents:
  appName: server
  backup_policy_name: bkp-policy-327-uai3047228-common
  custom_rg: rg-327-uai3026350-archive
  default_asgs:
    bastion_base: 'false'
    db_base: 'false'
    gehttp_internal: 'true'
    gessh_internal: 'true'
    gitend_http: 'true'
    linux_base: 'true'
    smtp_relay: 'false'
  env: dev
  image_name: GESOS-AZ-BASE-CENTOS7
  net_groups:
    - CA_NRGPOWR_NC_AZURE-PRDBASTION
  region: East US
  subcode: '327'
  subnet_name: Application-Subnet
  subscription_id: d0795f6d-b7a1-41a6-a156-ee5335433d9d
  uai: uai3026350
  vm_name: app-vm-test
  vm_size: Standard_D2as_v4
module: vmprov-dev-nix-1
org: 327-gp-azr-ops-dev
repo: uai3047228-ansible
resource: vm_gp_linux_standard
```

**Windows VM:**
```yaml
contents:
  appName: server
  backup_policy_name: bkp-policy-327-uai3047228-common
  custom_rg: rg-327-uai3047228-ansible-refactor
  default_asgs:
    bastion_base: false
    db_base: false
    gehttp_internal: true
    gessh_internal: true
    gitend_http: true
    smtp_relay: false
    windows_base: true
  env: dev
  image_name: GESOS-AZ-BASE-WINDOWS2019
  net_groups:
    - SVR_TCS_NIMBUS_2018_ADMIN
    - SVR_GE009000000_PWT_Migration_Factory
  region: East US
  subcode: '327'
  subnet_name: Application-Subnet
  subscription_id: d0795f6d-b7a1-41a6-a156-ee5335433d9d
  uai: uai3047228
  vm_name: app-vm-test
  vm_size: Standard_D2as_v4
module: vmprov-dev-win-1
org: 327-gp-azr-ops-dev
repo: uai3047228-ansible
resource: vm_gp_windows_standard
```