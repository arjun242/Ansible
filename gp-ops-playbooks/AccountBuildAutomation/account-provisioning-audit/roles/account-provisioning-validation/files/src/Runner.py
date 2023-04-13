import sys
import boto3
import boto3.session
import json
import os
from datetime import datetime
from IAMAuditer import IAMAuditer
from VPCAuditer import VPCAuditer
from SSMAuditer import SSMAuditer
from StacksAuditer import StacksAuditer
from MISCAuditer import MISCAuditer
from FileWriter import FileWriter
from SNSSender import SNSSender
import urllib3
import yaml


class Runner:

    """
    Runner class that orchestrates the account audit:
    1. Gathers output from CheckBucketPolicy.py
    2. Instantiates and runs all Audit classes
    3. Passes their output to the FileWriter class
    4. Pasess files produced to the SNSSender class to publish notificication.

    """

    def fetch_config_file(self):
        with open('/tmp/account-automation-folder/account-audit-service/config/ideal_account.yml', 'r') as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    def __init__(self, region_name, account_name, primary_role_arn, customConfig):

        # ignore insecure request warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # setup profile-name, session

        # profiles are not used now assume cross account role
        # self.profile_name = profile_name
        self.region_name = region_name
        self.account_name = account_name
        self.primary_role_arn = primary_role_arn
        self.customConfig = customConfig

        # check region name
        if self.region_name != 'us-east-1' and self.region_name != 'eu-west-1' and self.region_name != 'us-west-1' and self.region_name != 'ap-southeast-1':
            print('Usage: region name must be either us-east-1 or eu-west-1 or us-west-1 or ap-southeast-1.')
            exit(1)

        # assume role
        sts_client = boto3.client('sts')

        # asssume role object
        assumed_role_object = sts_client.assume_role(
            RoleArn=self.primary_role_arn,
            RoleSessionName="AssumeRoleSession1"
        )

        # From the response that contains the assumed role, get the temporary
        # credentials that can be used to make subsequent API calls
        credentials = assumed_role_object['Credentials']

        # setup session
        session = boto3.session.Session(aws_access_key_id=credentials['AccessKeyId'],
                                        aws_secret_access_key=credentials['SecretAccessKey'],
                                        aws_session_token=credentials['SessionToken'],
                                        region_name=self.region_name)

        # list of data objects
        json_objects = []

        # create account and time structure
        print("Getting Account Id...")
        self.account_id = session.client(
            'sts').get_caller_identity().get('Account')

        print("Creating Timestamp...")
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")
        account_and_time_data = {'AccountAndTimeData': {
            'AccountId': self.account_id, 'AccountName': self.account_name, 'Timestamp': timestamp}}
        json_objects.append(account_and_time_data)

        # setup output files
        json_file = self.account_id + '.json'
        log_file = self.account_id + '.txt'

        # gather information from CheckBucketPolicy script
        if os.path.exists('bucket-policies.txt'):

            logs_check = False
            artifacts_check = False
            eu_artifacts_check = False
            tools_check = False
            us_w_artifacts_check = False
            sec_check = False

            with open('bucket-policies.txt', 'r') as file:
                text = file.read()
                if 'gp-ops-ssm-logs-update=true' in text:
                    logs_check = True
                if 'gp-us-east-ops-automation-common-artifacts-update=true' in text:
                    artifacts_check = True
                if 'gp-us-east-ops-automation-common-tools-update=true' in text:
                    tools_check = True
                if 'gp-eu-west-ops-automation-common-artifacts-update=true' in text:
                    eu_artifacts_check = True
                if 'gp-us-west-ops-automation-common-artifacts=true' in text:
                    us_w_artifacts_check = True
                if 'uai3027632-pw-sec-automation-gp-ops=true' in text:
                    sec_check = True

            # create BucketPolicyUpdates structure
            inner_struct = {
                'gp-ops-ssm-logs': logs_check,
                'gp-us-east-ops-automation-common-artifacts': artifacts_check,
                'gp-us-east-ops-automation-common-tools': tools_check,
                'gp-eu-west-ops-automation-common-artifacts': eu_artifacts_check,
                'gp-us-west-ops-automation-common-artifacts': us_w_artifacts_check,
                'uai3027632-pw-sec-automation-gp-ops': sec_check
            }
            outer_struct = {'BucketPolicyUpdates': inner_struct}
            json_objects.append(outer_struct)

        else:
            print('ERROR: bucket-policies.txt does not exist.\nPlease run CheckBucketPolicy.py script before executing this.')
            exit(1)

        account_config = self.fetch_config_file()

        # run audits
        auditer = IAMAuditer(
            session=session, ideal_config=account_config['iam'])
        iam_data = auditer.return_data()
        json_objects.append(iam_data)

        auditer = VPCAuditer(
            session=session, ideal_config=account_config['vpc'], custom_config=self.customConfig['vpc'])
        vpc_data = auditer.return_data()
        json_objects.append(vpc_data)

        auditer = SSMAuditer(
            session=session, ideal_config=account_config['ssm'])
        ssm_data = auditer.return_data()
        json_objects.append(ssm_data)

        auditer = StacksAuditer(
            session=session, ideal_config=account_config['stacks'])
        stacks_data = auditer.return_data()
        json_objects.append(stacks_data)

        auditer = MISCAuditer(
            session=session, ideal_config=account_config['misc'])
        misc_data = auditer.return_data()
        json_objects.append(misc_data)

        # have FileWriter write json and text
        writer = FileWriter(json_objects, json_file, log_file)
        writer.write_json()
        writer.write_text()

        # send SNS notification
        # topic_arn = "arn:aws:sns:{0}:{1}:AccountAudit".format(
        #    self.region_name, self.account_id)
        # subject = "Account Audit: {0}".format(self.account_id)
        # text_file = "/tmp/account-automation-folder/account-audit-service/output/txt/{0}.txt".format(self.account_id)
        # json_file = "/tmp/account-automation-folder/account-audit-service/output/json/{0}.json".format(self.account_id)
        # sender = SNSSender(session=session, topic_arn=topic_arn, subject=subject, text_file=text_file, json_file=json_file)
        # sender.publish()

        # remove unnecessary file
        os.remove('bucket-policies.txt')
