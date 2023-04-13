import boto3
import sys
from os import path
from botocore.exceptions import ClientError
import json

"""
Script to check if gp-ops-ssm-logs, gp-us-east-ops-automation-common-artifacts,
and gp-us-east-ops-automation-common-tools bucket policies have been updated
to include permissions for a newly created account.

Usage: python CheckBucketPolicy.py <profile name> <account id>

"""

class CheckBucketPolicy:

    def __init__(self, account_id, gp_ops_audit_role_arn, region_name):

        # declare placeholders variables for account_id, role_arn, region_name
        self.account_id = account_id
        self.account_arn = 'arn:aws:iam::' + str(self.account_id) + ':root'
        self.gp_ops_audit_role_arn = gp_ops_audit_role_arn
        self.region_name = region_name

        # assume sts role
        sts_client = boto3.client('sts')

        # asssume role object
        assumed_role_object = sts_client.assume_role(
            RoleArn="arn:aws:iam::325381443140:role/hq/audit-fed",
            RoleSessionName="AssumeRoleSession1"
        )

        # From the response that contains the assumed role, get the temporary
        # credentials that can be used to make subsequent API calls
        credentials = assumed_role_object['Credentials']

        # declare S3 boto session based on assumed role credentials
        session = boto3.session.Session(aws_access_key_id=credentials['AccessKeyId'],
                                        aws_secret_access_key=credentials['SecretAccessKey'],
                                        aws_session_token=credentials['SessionToken'],
                                        region_name=self.region_name)
        
        # instantiate s3 boto session
        s3 = session.client('s3', verify=False)

        print('Checking S3 policy permissions...')



        # S3 buckets to check
        buckets = ['gp-ops-ssm-logs', 'gp-us-east-ops-automation-common-artifacts', 'gp-us-east-ops-automation-common-tools', 'gp-eu-west-ops-automation-common-artifacts', 'gp-us-west-ops-automation-common-artifacts', 'uai3027632-pw-sec-automation-gp-ops']
        

        with open('bucket-policies.txt', 'w') as file:
            for bucket in buckets:
                response = None
                try:
                    print("Attempting to fetch policy for {}".format(bucket))
                    # fetch bucket policy for current bucket in gp-ops account
                    response = s3.get_bucket_policy(Bucket=bucket)
                    # print("Success")
                except ClientError as e:
                    print("Exception occured")
                    print(e)
                    exit(1)

                # Check gp-ops-ssm-logs bucket policy
                if bucket == 'gp-ops-ssm-logs':
                    if response['Policy'] and 'Ansible Enable put from accounts' in response['Policy']:
                        put_permissions = response['Policy'].split('Ansible Enable put from accounts')[1].split('AWS')[1]
                        if self.account_arn in put_permissions:
                            file.write("{0}-update=true\n".format(bucket))
                        else:
                            file.write("{0}-update=false\n".format(bucket))

                # check gp-us-east-ops-automation-common-artifacts bucket policy
                elif bucket == 'gp-us-east-ops-automation-common-artifacts':
                    if response['Policy'] and 'Ansible Enable List Bucket from the Following VPC' in response['Policy']:
                        get_permissions = response['Policy'].split('Ansible Enable List Bucket from the Following VPC')[1].split('AWS')[1]
                        if self.account_arn in get_permissions:
                            file.write("{0}-update=true\n".format(bucket))
                        else:
                            file.write("{0}-update=false\n".format(bucket))
                
                # check gp-us-east-ops-automation-common-tools bucket policy
                elif bucket == 'gp-us-east-ops-automation-common-tools':
                    if response['Policy'] and 'Ansible Enable List from Following VPC' in response['Policy']:
                        get_permissions = response['Policy'].split('Ansible Enable List from Following VPC')[1].split('AWS')[1]
                        if self.account_arn in get_permissions:
                            file.write("{0}-update=true\n".format(bucket))
                        else:
                            file.write("{0}-update=false\n".format(bucket))

                # check gp-eu-west-ops-automation-common-artifacts bucket policy
                elif bucket == 'gp-eu-west-ops-automation-common-artifacts':
                    if response['Policy'] and 'Enable List Bucket from the following VPC' in response['Policy']:
                        get_permissions = response['Policy'].split('Enable List Bucket from the following VPC')[1].split('AWS')[1]
                        if self.account_arn in get_permissions:
                            file.write("{0}-update=true\n".format(bucket))
                        else:
                            file.write("{0}-update=false\n".format(bucket))

                # check gp-us-west-ops-automation-common-artifacts bucket policy
                elif bucket == 'gp-us-west-ops-automation-common-artifacts':
                    if response['Policy'] and 'Enable List Bucket from the Following VPC' in response['Policy']:
                        get_permissions = response['Policy'].split('Enable List Bucket from the Following VPC')[1].split('AWS')[1]
                        if self.account_arn in get_permissions:
                            file.write("{0}-update=true\n".format(bucket))
                        else:
                            file.write("{0}-update=false\n".format(bucket))
                
				# uai3027632-pw-sec-automation-gp-ops
                elif bucket == 'uai3027632-pw-sec-automation-gp-ops':
                    if response['Policy'] and 'EnableGetObjectFromFollowingVPC' in response['Policy']:
                        get_permissions = response['Policy'].split('EnableGetObjectFromFollowingVPC')[1].split('AWS')[1]
                        if self.account_arn in get_permissions:
                            file.write("{0}-update=true\n".format(bucket))
                        else:
                            file.write("{0}-update=false\n".format(bucket))

                else:
                    if response['Policy'] and 'Enable Get Object From Following VPC' in response['Policy']:
                        get_permissions = response['Policy'].split('Enable Get Object From Following VPC')[1].split('AWS')[1]
                        if self.account_arn in get_permissions:
                            file.write("{0}-update=true\n".format(bucket))
                        else:
                            file.write("{0}-update=false\n".format(bucket))







