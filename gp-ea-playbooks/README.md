# gp-ea-playbooks

This is an in-progress repo for playbooks. It includes playbooks intended for compliance services, inventory, platform and service.

- Compliance Playbooks:
   
   Roles : Contains the roles for the compliance services playbooks Cloudwatch-Alarm, CrowdStrike, ldap2fa, Qualys and Splunk
   
   It contains the main.yml files for Cloudwatch-Alarm, CrowdStrike, ldap2fa, Qualys and Splunk which when executed, will be trigger the respective roles 
   
   The folder also contains service-check.yml; which checks if the compliance services are installed or not and com-status-check.yml; which checks the status of the compliance  services 

- Inventory Playbooks:
   
   Contains the Ansible EC2 external inventory script settings

- Platform Playbooks:
   
   Will contain PLatform specific playbooks

- Service Playbooks:
   
   Contains the jenkins autodeployment scripts for execution and build

- Jenkins File: 
  
   Required for the Jenkins pipeline
