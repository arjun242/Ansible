import boto3
import json
from Helpers import Helpers
from botocore.exceptions import ClientError


class MISCAuditer:

    """
    Class that performs miscellaneous audit operations
    This includes:
    EBS volumes are being encrypted by default
    No public AMIs are in use
    Correct security config rules exist
    Correct DLM policies in place for snapshotting
    
    """

    def __init__(self, session, ideal_config):
        self.session = session
        self.ideal_config = ideal_config
        self.ec2 = self.session.resource('ec2')
        self.client = self.session.client('ec2')
        self.lamb = session.client('lambda')
        self.config = self.session.client('config')
        self.dlm = self.session.client('dlm', use_ssl=False)
        self.sns = self.session.client('sns')
        self.helpers = Helpers()
     

    def is_ebs_encrypted_by_default(self):

        print("Confirming EBS volumes are encrypted by default...")

        try:
            encrypted = self.client.get_ebs_encryption_by_default() 
            if encrypted:
                return True
            else:
                return False
        except ClientError as e:
            print(e)
            exit(1)

    def get_public_amis(self):

        print("Confirming AMIs in use are private...")
        
        # get all image ids from all instances
        image_ids = self.get_image_ids()

        # return all images that not private
        public_images = []
        for id in image_ids:
            image = self.ec2.Image(id)
            try:
                is_public = image.public
                if is_public:
                    public_images.append(str(image))
            except AttributeError as e:
                print("AMI encountered with no attributes.  Likely means a deregistered or deprecated AMI.")
                pass

        return public_images
    
    def get_missing_config_rules(self):

        print("Confirming config rules are launched...")

        # get required config rules
        required_rules = set(self.ideal_config['requiredConfigRules'])
        
        # get current config rules
        launched_rules = set()
        try:
            response = self.config.describe_config_rules()
        except ClientError as e:
            print(e)
            exit(1)

        if response['ConfigRules']: # null check
            for i in range(len(response['ConfigRules'])):
                rule = response['ConfigRules'][i]['ConfigRuleName']
                launched_rules.add(rule)

        # if multiple pages exist loop through them
        NextToken = self.helpers.next_token(response)
        while NextToken:
            try:
                response = self.config.describe_config_rules(NextToken=NextToken)
            except ClientError as e:
                print(e)
                exit(1)

            for i in range(len(response['ConfigRules'])):
                rule = response['ConfigRules'][i]['ConfigRuleName']
                launched_rules.add(rule)

            NextToken = self.helpers.next_token(response)
        
        return list(required_rules - launched_rules)
    
    def get_missing_backup_policies(self):

        pass
        # At the moment there is no way to uniquely identify DLM snapshot policies
        
    def get_missing_lambda_functions(self):

        print("Confirming Lambda Functions exist...")

        # required lambda functions
        required_lambda_functions = self.ideal_config['requiredLambdaFunctions']

        # get names of lambda functions in account
        current_functions = set()
        try:
            response = self.lamb.list_functions()
        except ClientError as e:
            print(e)
            exit(1)

        if response['Functions']: # null check
            for i in range(len(response['Functions'])):
                current_functions.add(response['Functions'][i]['FunctionName'].lower())
        
        # if multiple pages exist then loop through them
        NextMarker = self.helpers.next_marker(response)  
        while NextMarker:
            try:
                response = self.lamb.list_functions(Marker=NextMarker)
            except ClientError as e:
                print(e)
                exit(1)

            for i in range(len(response['Functions'])):
                current_functions.add(response['Functions'][i]['FunctionName'].lower()) 
            NextMarker = self.helpers.next_marker(response)    

        # return missing functions
        return list(required_lambda_functions - current_functions)

    def cloud_watch_topic_exists(self):

        print("Confirming CloudWatch SNS topic exists...")

        # loop through topics and find match
        try:
            response = self.sns.list_topics()
        except ClientError as e:
            print(e)
            exit(1)

        if response['Topics']:
            for i in range(len(response['Topics'])):
                if 'GpCloudWatchMetrics' in response['Topics'][i]['TopicArn']:
                    return True

        NextToken = self.helpers.next_token(response)
        while NextToken:
            try:
                response = self.sns.list_topics(NextToken=NextToken)
            except ClientError as e:
                print(e)
                exit(1)

            if response['Topics']:
                for i in range(len(response['Topics'])):
                    if 'CloudWatchMetrics' in response['Topics'][i]['TopicArn']:
                        return True
            NextToken = self.helpers.next_token(response)
        
        return False

    def return_data(self):

        # call all methods and return data
        missing_lambda_functions = self.get_missing_lambda_functions()
        ebs_encrypted = self.is_ebs_encrypted_by_default()
        public_amis = self.get_public_amis()
        missing_rules = self.get_missing_config_rules()
        sns_topic_exists = self.cloud_watch_topic_exists()
        inner_struct = {'MissingLambdaFunctions': missing_lambda_functions,'EBSEncryptionByDefault': ebs_encrypted, 'PublicImagesInUse': public_amis, 'MissingConfigRules': missing_rules, 'CloudWatchTopicExists': sns_topic_exists}
        outer_struct = {'Miscellaneous': inner_struct}
        return outer_struct

    # helper methods

    def get_image_ids(self):

        image_ids = set()
        instances = list(self.ec2.instances.all())
        for instance in instances:
            image_ids.add(instance.image_id)
        
        return image_ids

    def get_required_rules(self):

        # get rules from rules.txt file
        rules = set()
        with open('required-config-rules.txt', 'r') as file:
            for rule in file:
                rules.add(rule.strip())
        
        return rules

