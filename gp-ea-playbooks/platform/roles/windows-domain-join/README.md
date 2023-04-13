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
This playbook is used to join the target windows host to the specified domain.
- Scope: This playbook gets executed on the instances in running state identified by Ansible's Dynamic Inventory. Every time a job runs, the inventory gets refershed with the running instances.

## 2. Design
Below is the Flow Diagram for Windows Domain Join role.

![Flow Diagram](https://github.build.ge.com/gp-ansible-dev/gp-ea-dev-playbooks/blob/master/compliance/roles/Images/Windows_Domain_Join_FC.png)

## 3. Playbook Execution
 To execute this playbook: Run the 'pf-windows-domain-join.yml' file using the command > ***ansible-playbook pf-windows-domain-join.yml***

This playbook has been designed using roles. 
A role can be created using the command: ***ansible-galaxy init <ROLE_NAME>***
Upon creating a role, a default directory structure gets created.

## 4. Testing

| Test Case                                                       | Expected                                                                                                                                                                                                                                               | Actual Result                                                                                                                                                                                                                                                                   |   
| ----------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Instance not part of Domain with Root certificates installed    | Skips the tasks for installing the certificates. Performs ARS entry and joins the system to the domain using the credentials fetched. Reboots the instance. Adds the domain groups to the administrators group, if not already                         | If the necessary root certificates are present, skips tasks for installing the certificates. Performs ARS entry and joins the system to the domain using the credentials fetched. Reboots the instance.  Adds the domain groups to the administrators group, if not already     |
| Instance not part of Domain with Root certificates not installed| Downloads the certificates from S3 bucket and installs them. Performs ARS entry and joins the system to the domain using the credentials fetched.  Reboots the instance. Adds the domain groups to the administrators group, if not already            | Downloads the certificates from S3 bucket and installs them. Performs ARS entry and joins the system to the domain using the credentials fetched.  Reboots the instance. Adds the domain groups to the administrators group, if not already                                     |
| Instance part of Domain with Root certificates not installed    | Downloads the certificates from S3 bucket and installs them. Result for further tasks is printed as ok                                                                                                                                                 | Downloads the certificates from S3 bucket and installs them. Result for further tasks is printed as ok                                                                                                                                                                          |                                                                                                             |                                                                                         |           
| Instance part of Domain with Root certificates installed        | Skips the tasks for installing the certificates.  Result for further tasks is printed as ok                                                                                                                                                            | Skips the tasks for installing the certificates.  Result for further tasks is printed as ok                                                                                                                                                                                     |

## 5. Security Considerations
1. Ansible User: This playbook is designed to be executed on 'Ansible' user on the target host. This user will have full permissions and access on the host.

