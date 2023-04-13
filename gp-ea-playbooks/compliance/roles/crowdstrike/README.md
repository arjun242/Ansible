Author: Madhu Jha

Updated By: Suaad Sayyed

# Table of contents
1. Introduction
   - Scope
2. Design
3. Playbook Execution
4. Testing
5. Security Considerations

## 1. Introduction
This playbook is used to setup CrowdStrike on windows and linux hosts for existing and new instances.
- Scope: This playbook gets executed on the instances in running state identified by Ansible's Dynamic Inventory. Every time a job runs, the inventory gets refershed with the running instances.

## 2. Design
Below is the Flow Diagram for CrowdStrike role.

![Flow Diagram](https://github.build.ge.com/gp-ansible/gp-ea-playbooks/blob/master/compliance/roles/Images/CrowdStrike_FC.png)

## 3. Playbook Execution
 To execute this playbook: Run the 'com-crowdstrike.yml' file using the command > ***ansible-playbook com-crowdstrike.yml***

This playbook has been designed using roles. 
A role can be created using the command: ***ansible-galaxy init <ROLE_NAME>***
Upon creating a role, a default directory structure gets created.

## 4. Testing 

<p align="center"><strong>LINUX</strong></p>

| Test Case                                | Expected                                                                                                                                                                                                                                               | Actual Result                                                                                                                                                                                                                                        |   
| -----------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CrowdStrike is not installed             | If not existing, creates a directory ,downloads the package on master node and then copies it to the target host and installs it. Configures the CrowdStrike Agent with CustomerId and ActivationId and starts the service. Handler is notified.       | If not existing, creates a directory ,downloads the package on master node and then copies it to the target host and installs it. Configures the CrowdStrike Agent with CustomerId and ActivationId and starts the service. Handler is notified.     |
| CrowdStrike is installed                 | Skips the tasks that downloads and configures the CrowdStrike Agent with CustomerId and ActivationId. Starts the service.                                                                                                                              | Skips the tasks that downloads and configures the CrowdStrike Agent with CustomerId and ActivationId. Starts the service.                                                                                                                            |
| CrowdStrike is installed and not running | Skips the tasks that downloads and configures the CrowdStrike Agent with CustomerId and ActivationId. Starts the service.                                                                                                                              | Skips the tasks that downloads and configures the CrowdStrike Agent with CustomerId and ActivationId. Starts the service.                                                                                                                            |           
| When package is not updated              | If the existing package version does not match with the updated version, it will download and install the updated package.                                                                                                                             | If the existing package version does not match with the updated version, it will download and install the updated package.              

<p align="center"><strong>WINDOWS</strong></p>

| Test Case                                | Expected                                                                                                                                                                                                                                               | Actual Result                                                                                                                                                                                                     |   
| -----------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CrowdStrike is not installed             | If not existing, creates a directory and downloads the package on master node, copies it to the target host, installs and configures the CID. Deletes the installer file from target host. Starts the service.                                         | If not existing, creates a directory and downloads the package on master node, copies it to the target host, installs and configures the CID. Deletes the installer file from target host. Starts the service     |
| CrowdStrike is installed                 | Debug message is printed stating that CrowdStrike is installed. Skips the tasks that downloads and configures the CrowdStrike Agent with CustomerId. Starts the service                                                                                | Debug message is printed stating that CrowdStrike is installed. Skips the tasks that downloads and configures the CrowdStrike Agent with CustomerId. Starts the service                                           |
| CrowdStrike is installed and not running | Debug message is printed stating that CrowdStrike is installed. Skips the tasks that downloads and configures the CrowdStrike Agent with CustomerId.                                                                                                   | Debug message is printed stating that CrowdStrike is installed. Skips the tasks that downloads and configures the CrowdStrike Agent with CustomerId. Starts the service                                           |  
| When package is not updated                                     | If update=yes in vars folder, the block to download and install the package is executed. Service is started                                                                                                                                            | If update=yes in vars folder, the block to download and install the package is executed. Service is started                                |

## 5. Security Considerations
1. Ansible Vault to store confidential credentials: This playbook leverages the Ansible Vault to store and retrieve the CrowdStrike Customer ID. The secret.yml file in vars is encrypted and gets decrypted to fetch the data only at run-time only. A vault credential is created on the Ansible tower to decrypt the secrets.yml. Using this credential we can use the data inside the encrypted file in our playbook. 
  - ***Commands:***
     - ***Creating new encrypted file: ansible-vault create filename.yml***
     - ***Encrypting file: ansible-vault encrypt filename.yml*** 
     - ***Decrypting file: ansible-vault decrypt filename.yml*** 
     - ***View encrypted file: ansible-vault view filename.yml***
     - ***Executing playbook which uses encrypted file vars: ansible-playbook -i inventory_name playbook_name.yml --ask-vault-pass***  
2. Ansible User: This playbook is designed to be executed on 'Ansible' user on the target host. This user will have minimum permissions and access on the host.
3. Use of 'become' for privilege escalation: Where needed for root permissions on the host, become: yes is enabled for successful privilege escalation. This will enable smooth execution of the playbook tasks.
