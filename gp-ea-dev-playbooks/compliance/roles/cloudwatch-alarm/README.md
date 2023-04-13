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
This playbook is used to setup Amazon CloudWatch Agents on windows and linux hosts for existing and new instances.
- Scope: This playbook gets executed on the instances in running state identified by Ansible's Dynamic Inventory. Every time a job runs, the inventory gets refershed with the running instances.
 
 ## 2. Design
Below is the Flow Diagram for CloudWatch-Alarm role.

![Flow Diagram](https://github.build.ge.com/gp-ansible-dev/gp-ea-dev-playbooks/blob/master/compliance/roles/Images/CloudWatch-Alarm_FC.png)

## 3. Playbook Execution
 To execute this playbook: Run the 'com-cloudwatch-alarm.yml' file using the command > ***ansible-playbook com-cloudwatch-alarm.yml***

This playbook has been designed using roles. 
A role can be created using the command: ***ansible-galaxy init <ROLE_NAME>***
Upon creating a role, a default directory structure gets created.
 
## 4. Testing 
| Test Cases | Expected Output  | Actual Output  |
|:----------:|:----------------:|:--------------:|
| CloudWatch-Agent not installed, not configured and alarms not setup | It downloads the CWA Package from the URL specified in vars, installs it and delete the the package from target node. Templates the .json file and deletes the existing default config and restarts the agent. Gathers metadata from the instance level and IAM role secrets to use and set alarm metrics accordingly. | It downloads the CWA Package from the URL specified in vars, installs it and delete the the package from target node. Templates the .json file and deletes the existing default config and restarts the agent. Gathers metadata from the instance level and IAM role secrets to use and set alarm metrics accordingly. |
| CloudWatch-Agent installed, not configured and alarms not configured | Skips the block to download, install and delete the CWA. Templates the .json file and deletes the existing default config and restarts the agent. Gathers metadata from the instance level and IAM role secrets to use and set alarm metrics accordingly. | Skips the block to download, install and delete the CWA. Templates the .json file and deletes the existing default config and restarts the agent. Gathers metadata from the instance level and IAM role secrets to use and set alarm metrics accordingly. |
| CloudWatch-Agent installed, configured but alarms not configured | Skips the block to download, install and delete the CWA. Skips the task to configure agent. Gathers metadata from the instance level and IAM role secrets to use and set alarm metrics accordingly. | Skips the block to download, install and delete the CWA. Skips the task to configure agent. Gathers metadata from the instance level and IAM role secrets to use and set alarm metrics accordingly. |
| CloudWatch-Agent installed, configured and alarms are configured | Skips the block to download, install and delete the CWA. Skips the task to configure agent. Gathers metadata from the instance level, alarm metrics remain unchanged. | Skips the block to download, install and delete the CWA. Skips the task to configure agent. Gathers metadata from the instance level, alarm metrics remain unchanged. |
| CloudWatch-Agent installed, configured but the service is not running. | Skips the block to download, install and delete the CWA. Skips the task to configure agent. Starts the service. Gathers metadata from the instance level, IAM role secrets, alarm metrics remain unchanged. | Skips the block to download, install and delete the CWA. Skips the task to configure agent. Starts the service. Gathers metadata from the instance level, IAM role secrets, alarm metrics remain unchanged. |

 
## 5. Security Considerations
1. Ansible User: This playbook is designed to be executed on 'Ansible' user on the target host. This user will have minimum permissions and access on the host.
2. Use of 'become' for privilege escalation: Where needed for root permissions on the host, become: yes is enabled for successful privilege escalation. This will enable smooth execution of the playbook tasks.
