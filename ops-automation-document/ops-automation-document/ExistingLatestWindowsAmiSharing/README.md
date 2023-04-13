# Description: This ssm doc is responsible to share the latest existing windows AMI across the regions and it's corresonding accounts.


# Parameters:

LatestAMI: default: '{{ssm:/automation/ami/windows}}' description: Value of the latest AMI that needs to be shared across the accounts.


AMISharingRegAccList: default: '{{ssm:/automation/region-account}}' description:: region and corresponding accounts where AMI needs to be shared
