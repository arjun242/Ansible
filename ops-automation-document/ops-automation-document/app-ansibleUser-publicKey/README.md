This SSM document is responsible for creating the ansible user on linux and windows instances.

The ansible doc is baked as a part of the AMI factory for new instance configuration. Also, it can be run on existing instances to setup the ansible user.

*The ansible user password for windows user is pulled from Secrets Manager, which is hosted in gp-ops account: 
Secret name (automation/uai3026350-ansible-user)
Encryption key (automation-common-gp-ops)

To allow other accounts to pull the secrets from gp-ops, each account id is configured in the resource permission which would require to be updated everytime
a new account is created. Same changes will flow to the KMS key configuration as well.
