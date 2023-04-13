# Description: This ssm doc is responsible to share all existing ssm-doc which name starts with 'app' or 'shared'. 
documents will be shared across the regions and it's corresponding accounts which depends upon the parameter value.


# Parameters:

AMISharingRegAccList: default: '{{ssm:/automation/region-account}}' description: region and corresponding accounts where AMI needs to be shared
