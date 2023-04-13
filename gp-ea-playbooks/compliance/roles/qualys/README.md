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
This playbook is used to setup Qualys Cloud Agent on windows and linux hosts for existing and new instances.
- Scope: This playbook gets executed on the instances in running state identified by Ansible's Dynamic Inventory. Every time a job runs, the inventory gets refershed with the running instances.

## 2. Design
Below is the Flow Diagram for Qualys role.

![Flow Diagram](https://github.build.ge.com/gp-ansible/gp-ea-playbooks/blob/master/compliance/roles/Images/Qualys_FC.png)

## 3. Playbook Execution
 To execute this playbook: Run the 'com-qualys.yml' file using the command > ***ansible-playbook com-qualys.yml***

This playbook has been designed using roles. 
A role can be created using the command: ***ansible-galaxy init <ROLE_NAME>***
Upon creating a role, a default directory structure gets created.

## 4. Testing
<p align="center"><strong>LINUX</strong></p>

| Test Cases | Expected Output | Actual Output |
|:----------:|:---------------:|:-------------:|
| Qualys is not installed | If not existing, tasks to download and install the package is executed. Configures the Qualys Agent with CustomerId and ActivationId and starts the service. Handler is notified | As the package does not exist, tasks to download and install the package are executed. The Qualys Agent is Configured with CustomerId and ActivationId and the service is started. Handler is notified. |
| Qualys Service is not running | If service does not exist, tasks to download and install the package is executed. Configures the Qualys Agent with CustomerId and ActivationId and starts the service. Handler is notified | As the service does not exist, tasks to download and install the package are executed. The Qualys Agent is Configured with CustomerId and ActivationId and the service is started. Handler is notified. |
| Qualys is installed | A debug message is printed, skips all the tasks. Configures the Qualys Agent with CustomerId and ActivationId and starts the service. Handler is notified. | A debug message is printed, skips all the tasks. Configures the Qualys Agent with CustomerId and ActivationId and starts the service. Handlers is notified |
| Qualys is configured with wrong CID and ACID | A debug message is printed, skips all the tasks. Configures the Qualys Agent with CustomerId and ActivationId and starts the service. Handler is notified | A debug message is printed, skips all the tasks. Configures the Qualys Agent with CustomerId and ActivationId and starts the service. Handler is notified |
| When package is not updated | If the existing package version does not match with the updated version, it will download and install the updated package | The existing package version does not match with the updated version, it downloaded and installed the updated package |

---

<p align="center"><strong>WINDOWS</strong></p>

| Test Cases | Expected Output | Actual Output |
|:----------:|:---------------:|:-------------:|
| Qualys is not installed with correct CID and ACID | Block to match CID,ACID is skipped. Tasks to download and install package are executed. Configures the Qualys Agent with CustomerId and ActivationId and starts the service | Block to match CID,ACID is skipped. Tasks to download and install package are executed. Configured the Qualys Agent with CustomerId and ActivationId and started the service |
| Qualys is installed with correct CID and ACID | Block to match the instance CID,ACID with the CID and ACID placed in secret.yml is skipped. Further tasks inside the block will be skipped. Service will be started | Block to match the instance CID,ACID with the CID and ACID placed in secret.yml is skipped. Further tasks inside the block are skipped. Service is started |
| Qualys is installed with wrong CID and ACID | Tasks to compare the CID and ACID placed is executed. On mismatch, tasks inside the block will be executed and configure the Qualys Agent with correct CustomerId and ActivationId and start the service | Tasks to compare the CID and ACID placed is executed. On mismatch, tasks inside the block are executed and configured the Qualys Agent with correct CustomerId and ActivationId and started the service |
| Qualys not updated | If the update variable in vars is update: 'yes' then it will download, install and configure the latest package. Service is started | The update variable in vars is update: 'yes', it downloaded, installed and configured the latest package. Service is started | 

## 5. Security Considerations
1. Ansible Vault to store confidential credentials: This playbook leverages the Ansible Vault to store and retrieve the Qualys Customer ID and Qualys Activation ID. The secret.yml file in vars is encrypted and gets decrypted to fetch the data only at run-time only. A vault credential is created on the Ansible tower to decrypt the secrets.yml. Using this credential we can use the data inside the encrypted file in our playbook. 
  - ***Commands:***
     - ***Creating new encrypted file: ansible-vault create filename.yml***
     - ***Encrypting file: ansible-vault encrypt filename.yml*** 
     - ***Decrypting file: ansible-vault decrypt filename.yml*** 
     - ***View encrypted file: ansible-vault view filename.yml***
     - ***Executing playbook which uses encrypted file vars: ansible-playbook -i inventory_name playbook_name.yml --ask-vault-pass***  
2. Ansible User: This playbook is designed to be executed on 'Ansible' user on the target host. This user will have minimum permissions and access on the host.
3. Use of 'become' for privilege escalation: Where needed for root permissions on the host, become: yes is enabled for successful privilege escalation. This will enable smooth execution of the playbook tasks.
