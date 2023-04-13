##Description:
This SSM Doc is responsible to built a new base AMI with all the basic required packages and configurations, 
This will be built from the source GESOS AMI that will be published in each Month.

##Parameters:

AutomationAssumeRole:  default: "arn:aws:iam::{{global:ACCOUNT_ID}}:role/inf/ssm-ami" description: "(Required) The ARN of the role that allows Automation to perform the actions on your behalf."

InstanceType: default: t3.medium description: "(Optional) Type of instance to launch as the workspace host. Instance types vary by region. Default is t3.medium."

QualysActivationId: default: "{{ssm:/automation/qualys/activationid}}" description: "qualys activation id"

QualysCustomerId: default: "{{ssm:/automation/qualys/customerid}}" description: "qualys activation id"

SecurityGroup: default: "{{ssm:/automation/ami/sg}}" description: "Base SG Id for windows Instance"

SourceAmiId: default: ami-00142a31b38bf9a62 description: "(Required) The source Amazon Machine Image ID."

SubnetId: default: "{{ssm:/automation/ami/subnet}}" description: "Subnet to launch as the workspace host. Subnets vary by VPC."

TargetAmiName: default: "SSMWindowsAmi_from_SourceAmiId_on_{{global:DATE_TIME}}" description: "(Optional) The name of the new AMI that will be created. Default is a system-generated string including the source AMI id, and the creation time and date."

uai: default: uai3026350 description: "UAI to tag instance and AMI. Default is AUTO."

AMISharingRegAccList: default: '{{ssm:/automation/region-account}}' description: region and corresponding accounts where AMI needs to be shared



##Applicable Accounts [Tagging]:

|Accounts   | Applicable  |
| ------------ | ------------ |
| 325381443140  | Yes |
| 762713699569  | No |
| 538462866776  | No |
| 100148143185  | No |
| 372444449616  | No |
