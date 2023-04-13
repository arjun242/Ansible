##Description: 
This SSM Doc is responsible to built a new base AMI with all the basic required packages and configurations, 
This will be built from the source GESOS AMI that will be published in each Month, Here we are picking the latest GESOS ami through Lambda invoke.


##Parameters:

InstanceIamRole: default: ec2-ami-instance-profile

TargetAmiName: default: 'SSMLinuxAmi_from_SourceAMIID_on_{{global:DATE_TIME}}'

InstanceType: default: t3.medium

SubnetId: default: '{{ssm:/automation/ami/subnet}}'

uai: default: uai3026350

KeyName: default: '{{ssm:/automation/ami/base-key}}'

SecurityGroup: default: '{{ssm:/automation/ami/sg}}' description: Base SG Id for Linux Instance

BucketName: default: '{{ssm:/automation/ami/bucket}}' description: common bucket

QualysActivationId: default: '{{ssm:/automation/qualys/activationid}}' description: qualys activation id

QualysCustomerId: default: '{{ssm:/automation/qualys/customerid}}' description: qualys activation id

AMISharingRegAccList: default: '{{ssm:/automation/region-account}}' description: region and corresponding accounts where AMI needs to be shared

AMINAME: default: GESOS-AWS-BASE_CENTOS7 description: Source AMI Name

SourceAmiId: default: '{{ssm:/automation/ami/centos7}}' Description: Published the new AMI-ID that has been created after the execution.


##Applicable Accounts [Tagging]:


|Accounts   | Applicable  |
| ------------ | ------------ |
| 325381443140  | Yes |
| 762713699569  | No |
| 538462866776  | No |
| 100148143185  | No |
| 372444449616  | No |
