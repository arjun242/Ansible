import boto3
import re
import json
import os
from Helpers import Helpers
from botocore.exceptions import ClientError

class StacksAuditer:

    """
    Class that performs stack audit operations
    This includes:
    Check that KMS key exists
    Correct lambda functions exist
    Correct stacks exist
    Correct region for patch window
    Correct RDS subnet groups exist
    Correct RDS parameter groups exist
    
    """

    def __init__(self, session, ideal_config):
        self.session = session
        self.ideal_config = ideal_config
        self.region = self.session.region_name
        self.kms = session.client('kms')
        self.cloud_formation = session.client('cloudformation')
        self.ec2 = session.resource('ec2')
        self.rds = session.client('rds', verify=False)
        self.helpers = Helpers()

    def is_kms_key_created(self):

        print("Confirming KMS key exists...")
        
        # check to see whether the common-kms-key was created
        try:
            response = self.kms.list_aliases()
        except ClientError as e:
            print(e)
            exit(1) 

        if response['Aliases']: # null check
            for i in range(len(response.get('Aliases'))):
                key_alias = response.get('Aliases')[i].get('AliasName')
                if key_alias == 'alias/common-kms-key':
                    return True
    
        return False
        
    def get_missing_stacks(self):

        print("Confirming required stacks exist...")

        # get required stack sets
        required_stacks = self.ideal_config['requiredStacks']

        # get all current stacks
        current_stacks = self.get_stacks_list()
        missing_stacks = []
        for stack in required_stacks:

            # special case - this stack doesn't have a hash on the end
            if stack == 'export-vpc-default':
                if stack not in current_stacks:
                    missing_stacks.append(stack)

            # these stacks contain hashes
            else:
    
                # no need for regex here, finding substring of stack in each string
                matched = [s for s in current_stacks if stack in s]
                if not matched:
                    missing_stacks.append(stack)
        
        return missing_stacks
    
    def is_patch_window_region_correct(self):

        print("Confirming standard patch windows region...")

        # get stack list
        current_stacks = self.get_stacks_list()

        # get stack name with hash
        stack_name = 'StackSet-standard-patch-windows'
        pattern = re.compile(stack_name + "-[a-zA-Z0-9]{8,}-*")
        matched = list(filter(pattern.match, current_stacks))

        # if stack exists confirm it's in correct region
        if matched:
            stack_name = matched[0]

            try:
                response = self.cloud_formation.describe_stacks(StackName=stack_name)
            except ClientError as e:
                print(e)
                exit(1)

            logical_id = response['Stacks'][0]['StackId']
            region = logical_id.split(':')[3]

            # this check assumes the audit was begun in the correct region
            if region == self.region:
                    return True
        
        return False

    def get_missing_rds_subnet_groups(self):

        print("Confirming required RDS subnet groups exist...")

        # required rds subnet groups
        required_subnet_groups = self.ideal_config['requiredSubnetGroups']

        # get current rds subnet groups
        current_subnet_groups = []
        try:
            response = self.rds.describe_db_subnet_groups()
        except ClientError as e:
            print(e)
            exit(1)
        if response['DBSubnetGroups']: # null check
            for i in range(len(response['DBSubnetGroups'])):
                current_subnet_groups.append(response['DBSubnetGroups'][i]['DBSubnetGroupName'])

        # check if required groups exist
        for subnet_group in required_subnet_groups:
            status = None
            pattern = re.compile(subnet_group + "-[a-zA-Z0-9]{13,}")
            match = list(filter(pattern.match, current_subnet_groups))
            if match:
                index = current_subnet_groups.index(match[0])
                status = response['DBSubnetGroups'][index]['SubnetGroupStatus']

            # if subnet group exists remove it from the list
            if status == 'Complete':
                required_subnet_groups.remove(subnet_group)
        
        # required list now only contains missing subnet groups
        return required_subnet_groups
    
    def get_missing_rds_parameter_groups(self):

        print("Confirming required RDS parameter groups exist...")

        # get required param groups
        required_param_groups = set()
        for group in self.ideal_config['requiredRDSParameterGroups']:
            required_param_groups.add(group.strip())
        
        # get current param groups and remove prefix and hash
        current_param_groups = set()
        try:
            response = self.rds.describe_db_parameter_groups() 
        except ClientError as e:
            print(e)
            exit(1)
        
        if response['DBParameterGroups']: # null check
            for i in range(len(response['DBParameterGroups'])):
                #remove prefix and hash and add to current groups
                if 'stackset-dbss-rds' in response['DBParameterGroups'][i]['DBParameterGroupName']: 
                    group_name = response['DBParameterGroups'][i]['DBParameterGroupName'].split('-')[-2]
                    current_param_groups.add(group_name)
        
        # loop through more pages if necessary
        Marker = self.helpers.marker(response)
        while Marker:

            try:
                response = self.rds.describe_db_parameter_groups(Marker=Marker) 
            except ClientError as e:
                print(e)
                exit(1)
        
            if response['DBParameterGroups']: # null check
                for i in range(len(response['DBParameterGroups'])):
                    #remove prefix and hash and add to current groups
                    if 'stackset-dbss-rds' in response['DBParameterGroups'][i]['DBParameterGroupName']: 
                        group_name = response['DBParameterGroups'][i]['DBParameterGroupName'].split('-')[-2]
                        current_param_groups.add(group_name)
            
            Marker = self.helpers.marker(response)
        
        return list(required_param_groups - current_param_groups)

    def get_missing_rds_option_groups(self):

        print("Confirming required RDS option groups exist...")

        # get required option groups
        required_option_groups = set()
        for group in self.ideal_config['requiredRDSOptionGroups']:
            required_option_groups.add(group.strip())
        
        # get current option groups and remove prefix and hash
        current_option_groups = set()
        try:
            response = self.rds.describe_option_groups() 
        except ClientError as e:
            print(e)
            exit(1)
        
        if response['OptionGroupsList']: # null check
            for i in range(len(response['OptionGroupsList'])):
                #remove prefix and hash and add to current groups
                if 'stackset-dbss-rds' in response['OptionGroupsList'][i]['OptionGroupName']: 
                    group_name = response['OptionGroupsList'][i]['OptionGroupName'].split('-')[-2]
                    current_option_groups.add(group_name)
        
        # loop through more pages if necessary
        Marker = self.helpers.marker(response)
        while Marker:

            try:
                response = self.rds.describe_option_groups(Marker=Marker) 
            except ClientError as e:
                print(e)
                exit(1)
        
            if response['OptionGroupsList']: # null check
                for i in range(len(response['OptionGroupsList'])):
                    #remove prefix and hash and add to current groups
                    if 'stackset-dbss-rds' in response['OptionGroupsList'][i]['OptionGroupName']: 
                        group_name = response['OptionGroupsList'][i]['OptionGroupName'].split('-')[-2]
                        current_option_groups.add(group_name)
            
            Marker = self.helpers.marker(response)
        
        return list(required_option_groups - current_option_groups)

    def return_data(self):

        # call all methods and return data
        missing_stacks = self.get_missing_stacks()
        patch_window_region = self.is_patch_window_region_correct()
        kms_key_created = self.is_kms_key_created()
        missing_rds_subnet_groups = self.get_missing_rds_subnet_groups()
        missing_rds_parameter_groups = self.get_missing_rds_parameter_groups()
        missing_rds_option_groups = self.get_missing_rds_option_groups()
        inner_struct = {'MissingStacks': missing_stacks, 'MissingRDSSubnetGroups': missing_rds_subnet_groups, 'MissingRDSParameterGroups': missing_rds_parameter_groups, 'MissingRDSOptionGroups': missing_rds_option_groups, 'PatchWindowRegionCorrect': patch_window_region, 'KMSKeyCreated': kms_key_created}
        outer_struct = {'Stacks': inner_struct}
        return outer_struct

    # Helper Methods

    def get_stacks_list(self):

        stacks_list = list()

        # get first page of stackssets and retreive stack names
        try:
            response = self.cloud_formation.list_stacks( 
                StackStatusFilter=self.ideal_config['stackStatusFilter']
            )
        except ClientError as e:
            print(e)
            exit(1)

        if response['StackSummaries']: # null check
            for i in range(len(response['StackSummaries'])):
                stacks_list.append(response['StackSummaries'][i]['StackName'])

        # loop through the the remaining pages of stacksets and retrieve their names
        NextToken = self.helpers.next_token(response)
        while NextToken:
            try:
                response = self.cloud_formation.list_stacks( 
                    StackStatusFilter=self.ideal_config['stackStatusFilter'],
                    NextToken=NextToken
                )
            except ClientError as e:
                print(e)
                exit(1)
                
            for i in range(len(response['StackSummaries'])):
                stacks_list.append(response['StackSummaries'][i]['StackName'])
            
            NextToken = self.helpers.next_token(response)
        
        return stacks_list


