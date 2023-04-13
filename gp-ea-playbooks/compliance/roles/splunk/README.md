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
This playbook is used to setup Splunk on windows and linux hosts for existing and new instances.
 - Scope: This playbook gets executed on the instances in running state identified by Ansible's Dynamic Inventory. Every time a job runs, the inventory gets refershed with the running instances.

## 2. Design
Below is the Flow Diagram for Splunk role.

![Flow Diagram](https://github.build.ge.com/gp-ansible/gp-ea-playbooks/blob/master/compliance/roles/Images/Splunk_FC.png)

## 3. Playbook Execution
Run the install_splunk.yml file using the command: ***ansible-playbook install_splunk.yml*** to execute this playbook.

This playbook has been designed using roles. A role can be created using the command: ***ansible-galaxy init <ROLE_NAME>***
Upon creating a role, a default directory structure gets created.

## 4. Testing
| Test Cases  | Expected Output   | Actual Output  |
|:-----------:|:-----------------:|:--------------:|
| Splunk is already installed and properly configured | A debug message will be printed. Tasks to download and Install are skipped. Configuration files will remain unchanged and task execution will result 'OK'. Shell command which enables boot start will get executed | A debug message is printed. Tasks to download and Install are skipped. Configuration files remained unchanged and task execution resulted 'OK'. Shell command which enables boot start got executed |
| Splunk is not installed | Tasks to download and Install Splunk Forwarder will be executed. The configuration files will be templated on the target hosts and handler is notified. Boot start will be enabled. Handler will be executed only once at the end of complete execution | Tasks to download and Install Splunk Forwarder are executed. The configuration files are templated on the target hosts and handler got notified. Boot start is enabled. Handler is executed only once at the end of complete execution |
| Configuration files are not present  | The conf files will be templated on the target host with proper configuration parameters and handler will be executed only once at the end of complete execution | The conf files are templated on the target host with proper configuration parameters and handler is executed only once at the end of complete execution |
| Configuration files have wrong data parameters | The conf file with wrong data will be templated with correct data parameters and handler will be executed only once at the end of complete execution | The conf file with wrong data is templated with correct data parameters and handler is executed only once at the end of complete execution |
| Required directories are not created  | The required directories will be created | The required directories are created |
| Package is installed but the service is stopped | Splunk will be started | Splunk is started |
| When package is not updated (Linux) | If the existing package version does not match with the updated version, it will download and install the updated package | As the existing package version does not match with the updated version, it downloaded and installed the updated package |
| Windows Package is not updated | If the update variable in vars is update: 'yes' then it will download, install and configure the latest package. Service is started | The update variable in vars is update: 'yes', it downloaded, installed and configured the latest package. Service is started | 

## 5. Security Considerations
1. Ansible Vault to store confidential credentials: This playbook leverages the Ansible Vault to store and retrieve the confidential data for config files. The secret.yml file in vars is encrypted and gets decrypted to fetch the data only at run-time only. A vault credential is created on the Ansible tower to decrypt the secrets.yml. Using this credential we can use the data inside the encrypted file in our playbook. 
  - ***Commands:***
     - ***Creating new encrypted file: ansible-vault create filename.yml***
     - ***Encrypting file: ansible-vault encrypt filename.yml*** 
     - ***Decrypting file: ansible-vault decrypt filename.yml*** 
     - ***View encrypted file: ansible-vault view filename.yml***
     - ***Executing playbook which uses encrypted file vars: ansible-playbook -i inventory_name playbook_name.yml --ask-vault-pass***  
2. Ansible User: This playbook is designed to be executed on 'Ansible' user on the target host. This user will have minimum permissions and access on the host.
3. Use of 'become' for privilege escalation: Where needed for root permissions on the host, become: yes is enabled for successful privilege escalation. This will enable smooth execution of the playbook tasks.
