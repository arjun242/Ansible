import json

class FileWriter:

    """
    Class to write the results of the audit.
    Writes results to a json file and a text file

    """

    def __init__(self, data, json_filename, log_filename):

        self.data = data
        self.json_filename = json_filename
        self.log_filename = log_filename

    
    def write_json(self):

        # make readable json and write it
        pretty_json = json.dumps(self.data, indent=2)
        with open('/tmp/account-automation-folder/account-audit-service/output/json/' + self.json_filename, 'w') as file:
            file.write(pretty_json)


    def write_text(self):
        
        with open('/tmp/account-automation-folder/account-audit-service/output/txt/' + self.log_filename, 'w') as file:

            # loop through data and write each section
            for i in range(len(self.data)):

                # get account and time info
                if 'AccountAndTimeData' in self.data[i]:
                    self.write_account_and_time(self.data[i], file)

                # get gp-ops bucket permissions
                elif 'BucketPolicyUpdates' in self.data[i]:
                    self.write_bucket_policy(self.data[i], file)

                # get IAM info and write it
                elif 'IAM' in self.data[i]:
                    self.write_iam(self.data[i], file)

                # get VPC info and write it
                elif 'VPC' in self.data[i]:
                    self.write_vpc(self.data[i], file)

                # get SSM info and write it
                elif 'SSM' in self.data[i]:
                    self.write_ssm(self.data[i], file)

                # get Stacks info and write it
                elif 'Stacks' in self.data[i]:
                    self.write_stacks(self.data[i], file)
                
                # get other info and write it
                elif 'Miscellaneous' in self.data[i]:
                    self.write_misc(self.data[i], file)

                
    # helper writers 

    def write_account_and_time(self, struct, file):

        # write account id and timestamp
        acct_time = struct['AccountAndTimeData']
        account_id = acct_time['AccountId']
        timestamp = acct_time['Timestamp']
        file.write('ACCOUNT AUDIT REPORT:\n')
        file.write("AccountId: {0}\n".format(account_id))
        file.write("Timestamp: {0}\n".format(timestamp))

        # also write reminders manual audit steps

        file.write("\n********** MANUAL AUDIT STEPS **********\n\n")
        file.write("1. NACL must be approved by EA team\n\n")
        file.write("2. New account Splunk request must be setup\n\n")
        file.write("3. GitHub org associated with account exists\n\n")
        file.write("4. infra-cf-templates repo and nacl-cf-templates repo within that GitHub org\n\n")
        file.write("5. CI/CD pipeline setup for apps team to use (Jenkinsfile) and Jenkins instance in place\n\n")
        file.write("6. Confirm that a join has been performed for windows active directory\n")


    def write_bucket_policy(self, struct, file):
        
        # write bucket policies status
        is_logs_bucket_updated = struct['BucketPolicyUpdates']['gp-ops-ssm-logs']
        is_us_e_artifacts_bucket_updated = struct['BucketPolicyUpdates']['gp-us-east-ops-automation-common-artifacts']
        is_tools_bucket_updated = struct['BucketPolicyUpdates']['gp-us-east-ops-automation-common-tools']
        is_eu_w_artifacts_bucket_updated = struct['BucketPolicyUpdates']['gp-eu-west-ops-automation-common-artifacts']
        is_us_w_artifacts_bucket_updated = struct['BucketPolicyUpdates']['gp-us-west-ops-automation-common-artifacts']
        is_sec_bucket_updated = struct['BucketPolicyUpdates']['uai3027632-pw-sec-automation-gp-ops']

        file.write("\n********** Bucket Policy Section **********\n\n")
        file.write("gp-ops-ssm-logs Bucket Policy Updated: {0}\n\n".format(is_logs_bucket_updated))
        file.write("gp-us-east-ops-automation-common-artifacts Bucket Policy Updated: {0}\n\n".format(is_us_e_artifacts_bucket_updated))
        file.write("gp-us-east-ops-automation-common-tools Bucket Policy Updated: {0}\n".format(is_tools_bucket_updated))
        file.write("gp-eu-west-ops-automation-common-artifacts Bucket Policy Updated: {0}\n".format(is_eu_w_artifacts_bucket_updated))
        file.write("gp-us-west-ops-automation-common-artifacts Bucket Policy Updated: {0}\n".format(is_us_w_artifacts_bucket_updated))
        file.write("uai3027632-pw-sec-automation-gp-ops Bucket Policy Updated: {0}\n".format(is_sec_bucket_updated))

    def write_iam(self, struct, file):
        
        iam = struct['IAM']
        num_missing_roles = len(iam['MissingRoles'])
        num_missing_policies = len(iam['MissingPolicies'])
        
        file.write("\n********** IAM Section **********\n")

        # write missing roles
        file.write("\nMissing Roles: {0}\n".format(num_missing_roles))
        for role in iam['MissingRoles']:
            file.write(role + "\n")
        
        # write missing policies
        file.write("\nMissing Policies: {0}\n".format(num_missing_policies))
        for policy in iam['MissingPolicies']:
            file.write(policy + "\n")

    def write_vpc(self, struct, file):

        # get data to write
        vpc = struct['VPC']
        num_missing_sec_groups = len(vpc['MissingSecurityGroups'])
        num_missing_subnets = len(vpc['MissingSubnets'])
        num_missing_route_tables = len(vpc['MissingRouteTables'])
        vpc_exists = vpc['NonDefaultVPCExists']
        inet_gateway_exists = vpc['InternetGateway']
        nat_gateway_exists = vpc['NatGateway']

        file.write("\n********** VPC Section **********\n")
        
        # write missing security groups
        file.write("\nMissing Security Groups: {0}\n".format(num_missing_sec_groups))
        for group in vpc['MissingSecurityGroups']:
            file.write(group + "\n")

        # write missing subnets
        file.write("\nMissing Subnets: {0}\n".format(num_missing_subnets))
        for subnet in vpc['MissingSubnets']:
            file.write(subnet + "\n")

        # write missing route tables
        file.write("\nMissing Route Tables: {0}\n".format(num_missing_route_tables))
        for table in vpc['MissingRouteTables']:
            file.write(table + "\n")

        # write vpc, inet and nat gateway info
        file.write("\nNon Default VPC Exists: {0}\n".format(vpc_exists))
        file.write("\nInternet Gateway Exists: {0}\n".format(inet_gateway_exists))
        file.write("\nNat Gateway Exists: {0}\n".format(nat_gateway_exists))

    def write_ssm(self, struct, file):
        
        # get data to write
        ssm = struct['SSM']
        num_missing_documents = len(ssm['MissingDocuments'])
        num_erroneous_assocations = len(ssm['ErroneousAssociations'])
        num_erroneous_parameters = len(ssm['ErroneousSSMParameters'])


        file.write("\n********** SSM Section **********\n")
        
        # write missing security groups
        file.write("\nMissing Documents: {0}\n".format(num_missing_documents))
        for doc in ssm['MissingDocuments']:
            file.write(doc + "\n")

        # write mainteance window status
        file.write("\nMaintenance Window Status:\n")
        for k,v in ssm['MaintenanceWindowStatus'].items():
            file.write(k + " : " + v + "\n\n")

        # write erroneous associations
        file.write("\nErroneous Associations: {0}\n".format(num_erroneous_assocations))
        for k,v in ssm['ErroneousAssociations'].items():
            file.write(k + " : " + v + "\n\n")

        # write erroneous SSM parameters
        file.write("\nErroneous SSM Parameters: {0}\n".format(num_erroneous_parameters))
        for k,v in ssm['ErroneousSSMParameters'].items():
            file.write(k + " : " + v + "\n")
           

    def write_stacks(self, struct, file):

        # get data to write
        stacks = struct['Stacks']
        num_missing_stacks = len(stacks['MissingStacks'])
        num_missing_rds_subnet_groups = len(stacks['MissingRDSSubnetGroups'])
        num_missing_rds_param_groups = len(stacks['MissingRDSParameterGroups'])
        num_missing_rds_option_groups = len(stacks['MissingRDSOptionGroups'])
        patch_window_region_correct = stacks['PatchWindowRegionCorrect']
        kms_key_created = stacks['KMSKeyCreated']

        file.write("\n********** Stacks Section **********\n")

        # write missing stacks
        file.write("\nMissing stacks: {0}\n".format(num_missing_stacks))
        for stack in stacks['MissingStacks']:
            file.write(stack + "\n")

        # write missing RDS subnet groups
        file.write("\nMissing RDS subnet groups: {0}\n".format(num_missing_rds_subnet_groups))
        for subnet_group in stacks['MissingRDSSubnetGroups']:
            file.write(subnet_group + "\n")

        # write missing RDS parameter groups
        file.write("\nMissing RDS parameter groups: {0}\n".format(num_missing_rds_param_groups))
        for param_group in stacks['MissingRDSParameterGroups']:
            file.write(param_group + "\n")

        # write missing RDS option groups
        file.write("\nMissing RDS option groups: {0}\n".format(num_missing_rds_option_groups))
        for option_group in stacks['MissingRDSOptionGroups']:
            file.write(option_group + "\n")

        # write key and patch window info
        file.write("\nKMS Key Created: {0}\n".format(kms_key_created))
        file.write("\nPatch Window Region Correct: {0}\n".format(patch_window_region_correct))


    def write_misc(self, struct, file):

        # get data to write
        misc = struct['Miscellaneous']
        num_missing_lambdas = len(misc['MissingLambdaFunctions'])
        num_public_images_in_use = len(misc['PublicImagesInUse'])
        num_missing_rules = len(misc['MissingConfigRules'])
        ebs_default_encryption = misc['EBSEncryptionByDefault']
        sns_topic_exists = misc['CloudWatchTopicExists']
            
        file.write("\n********** Miscellaneous Section **********\n")

         # write missing lambdas
        file.write("\nMissing Lambda Functions: {0}\n".format(num_missing_lambdas))
        for lamb in misc['MissingLambdaFunctions']:
            file.write(lamb + "\n")
        
        # write missing rules
        file.write("\nMissing Config Rules: {0}\n".format(num_missing_rules))
        for rule in misc['MissingConfigRules']:
            file.write(rule + "\n")

        # write missing rules
        file.write("\nPublic Images In Use: {0}\n".format(num_public_images_in_use))
        for image in misc['PublicImagesInUse']:
            file.write(image + "\n")

        # write ebs encryption info
        file.write("\nEBS Encryption by Default: {0}\n".format(ebs_default_encryption))

        # write cloud watch topic info
        file.write("\nCloud Watch Topic exists: {0}\n".format(sns_topic_exists))
        
