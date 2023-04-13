Description:  This is an Automation ssm document which is responsible to release WebHost AMI's across the accounts.
It takes the latest GESOS WebHost ami as an Input and Install basic sofwares and packages that we are doing through our AMI-Factory.

Ref: https://devcloud.swcoe.ge.com/devspace/display/WZSLF/WebHostAMI+AMI

While execution following SSM-Parameters needs to be updated carefully:

  WebHostAMIID: This is source GESOS WebHost AMI, which is taken as na input.
    type: String
    default: GESOS-AWS-JBOSS_CENTOS7
    description: 'Initial name of the WebHostAMI here just update value as "JBOSS_RHEL7", "APACHE_CENTOS7", "APACHE_RHEL7"'

Here we have to update the default value as per the AMI which we wish to release, so just need to update the last two <APP-Name>_<Platform>
like for Apache centos7 "GESOS-AWS-APACHE_CENTOS7", for Jboss rhel7 "GESOS-AWS-JBOSS_RHEL7".

  TargetAmiName: This is the target GP AMI which will be created from the source AMI
  
    default: 'GP-GESOS-AWS-JBOSS_CENTOS7_on_{{global:DATE_TIME}}'
    
    description: 'The name of the new AMI that will be created. here just update value as "JBOSS_RHEL7", "APACHE_CENTOS7", "APACHE_RHEL7"'
   
Here we have to update the default value as per the AMI which we wish to release, so just need to update the last two <APP-Name>_<Platform>
like for Apache centos7 "GESOS-AWS-APACHE_CENTOS7", for Jboss rhel7 "GESOS-AWS-JBOSS_RHEL7".

