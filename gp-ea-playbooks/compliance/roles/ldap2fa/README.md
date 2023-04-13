Author: Madhu Jha

Updated By: Prajwal Patil

# Table of contents
1. Introduction
   - Scope
2. Design
3. Playbook Execution
4. Testing
5. Security Considerations

## 1. Introduction
This playbook is used to setup LDAP-2FA authentication on linux hosts for existing and new instances. 
- Scope: This playbook gets executed on the instances in running state identified by Ansible's Dynamic Inventory. Every time a job runs, the inventory gets refershed with the running instances and only where **tag 'mfa' doesn't exist or 'mfa==enabled'**

## 2. Design
Below is the Flow Diagram for LDAP-2FA role.

![Flow Diagram](https://github.build.ge.com/gp-ansible/gp-ea-playbooks/blob/master/compliance/roles/Images/LDAP_FC.png)

## 3. Playbook Execution
 To execute this playbook: Run the 'com-ldap2fa.yml' file using the command > ***ansible-playbook com-ldap2fa.yml***

This playbook has been designed using roles. 
A role can be created using the command: ***ansible-galaxy init <ROLE_NAME>***
Upon creating a role, a default directory structure gets created.

## 4. Testing
| Test Cases | Expected Output | Actual Output |
|:----------:|:---------------:|:-------------:|
| LDAP-2FA is not enabled, appConfig exists | Tags from the instance will be fetched. If it is successfull, and the mfa == enabled, the LDAP role will be called. Required packages will be installed and directories will be created. As appConfig exists, netgroups inside appConfig will be added to conf files. Templates will be placed in the target, binary files will be copied, certs will be updated and services will be restarted with boot start enabled | Tags from the instance are fetched. It is successfull, and the mfa == enabled, the LDAP role is called. Required packages are installed and directories are created. The file appConfig exists, netgroups inside the appConfig are added to conf files. Templates are placed in the target, binary files are copied, certs are updated and services are restarted with boot start enabled |
| LDAP-2FA is not enabled, appConfig does not exists | Tags from the instance will be fetched. If it is successfull, and the mfa == enabled, the LDAP role will be called. Required packages will be installed and directories will be created. As appConfig does not exists, default netgroups will be added to conf files. Templates will be placed in the target, binary files will be copied, certs will be updated and services will be restarted with boot start enabled  | Tags from the instance are fetched. It is successfull, and the mfa == enabled, the LDAP role is called. Required packages are installed and directories are created. The file appConfig does not exists, default netgroups are added to conf files. Templates are placed in the target, binary files are copied, certs are updated and services are restarted with boot start enabled  |
| LDAP-2FA is enabled, appConfig exists | Tags from the instance will be fetched. If it is successfull, and the mfa == enabled, the LDAP role will be called. No changes will be made if all the config files contains correct data and services will be restarted | Tags from the instance are fetched. It is successfull, and the mfa == enabled, the LDAP role is called. No changes made to the config files because it contains correct data and services are restarted |
| LDAP-2FA is enabled, appConfig does not exists | Tags from the instance will be fetched. If it is successfull, and the mfa == enabled, the LDAP role will be called. Config files will be placed with default netgroups and services will be restarted | Tags from the instance are fetched. It is successfull, and the mfa == enabled, the LDAP role is called. Config files are placed with default netgroups and services are restarted |
| Fetching tags fails | The role will still be called and executed | The role is called and executed |
| mfa == disabled | The role will not be executed on it | The role did not execute on target host |
| Config files have incorrect data | If the appConfig file is present, playbook will template all the conf file with correct data according to the appConfig, if not, then it will place the default groups in the files | The appConfig file is present, playbook templated all the conf file with correct data according to the appConfig |

## 5. Security Considerations
1. Ansible Vault to store confidential credentials: This playbook leverages the Ansible Vault to store and retrieve the confidential secret keys for various config files. The secrets.yml file in vars is encrypted and gets decrypted to fetch the data only at run-time only. A vault credential is created on the Ansible tower to decrypt the secrets.yml. Using this credential we can use the data inside the encrypted file in our playbook. 
  - ***Commands:***
     - ***Creating new encrypted file: ansible-vault create filename.yml***
     - ***Encrypting file: ansible-vault encrypt filename.yml*** 
     - ***Decrypting file: ansible-vault decrypt filename.yml*** 
     - ***View encrypted file: ansible-vault view filename.yml***
     - ***Executing playbook which uses encrypted file vars: ansible-playbook -i inventory_name playbook_name.yml --ask-vault-pass***  
2. Ansible User: This playbook is designed to be executed on 'Ansible' user on the target host. This user will have minimum permissions and access on the host.
3. Use of 'become' for privilege escalation: Where needed for root permissions on the host, become: yes is enabled for successful privilege escalation. This will enable smooth execution of the playbook tasks.

***Note: All the required data for the templates will be fetched from either set_fact task, main.yml or secrets.yml placed in vars folder***
