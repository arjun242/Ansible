import boto3
import json
from Helpers import Helpers
from botocore.exceptions import ClientError


class VPCAuditer:

    """
    Class that performs Audit of VPC configuration.
    This includes:
    Non-default VPC exists
    Correct subnets exist
    Correct security groups exist
    Correct route tables exist
    NAT and Internet gateway is attached to non-default VPC
    
    """

    def __init__(self, session, ideal_config, custom_config):
        self.session = session
        self.ideal_config = ideal_config
        self.ec2 = self.session.resource('ec2')
        self.client = self.session.client('ec2')
        self.custom_config = custom_config
        self.helpers = Helpers()

    def vpc_exists(self):
        
        print("Confirming non-default VPC exists...")

        # if the helper method returns an id, a non-default vpc exists
        vpc_id = self.helpers.get_non_default_vpc_id(self.ec2)
        if vpc_id:
            return True
        
        return False
        
    def get_missing_security_groups(self):

        print("Confirming security groups exist...")

        # get security group names
        try:
            sec_group_list = list(self.ec2.security_groups.all())
        except ClientError as e:
            print(e)
            exit(1)

        sec_group_names = [group.group_name.lower() for group in sec_group_list] # get security group names in lower case
        required_sec_groups = [group.lower() for group in self.ideal_config['requiredSecurityGroups']]
        missing_security_groups = []

        # check security groups against requirements
        for group in required_sec_groups:
            if group not in sec_group_names:
                missing_security_groups.append(group)

        return missing_security_groups

    def get_missing_subnets(self):

        print("Confirming subnets exist...")

        # fetch expected subnet types for account
        expected_subnet_types = self.custom_config['expectedSubnets']
        try:
            subnet_list = list(self.ec2.subnets.all())
        except ClientError as e:
            print(e)
            exit(1)

        current_subnet_types = set()

        # check subnets against requirements
        for subnet in subnet_list:
            if subnet.tags: #null check
                for tag in subnet.tags:
                    if tag['Key'] == 'SubnetType':
                        current_subnet_types.add(tag['Value'])
        
        return list(expected_subnet_types), list(expected_subnet_types - current_subnet_types)

    def get_missing_route_tables(self):	

        print("Confirming route tables exist...")	

        # get route tables
        try:	
            route_table_list = list(self.ec2.route_tables.all())
        except ClientError as e:
            print(e)
            exit(1)	
            
        # consider case-discrepancies in route table names    
        required_tables = set([table.lower() for table in list(self.ideal_config['requiredTables'])])	
        current_tables = set()	

        # check route tables against requirements	
        for table in route_table_list:	
            if table.tags: #null check
                for tag in table.tags:
                    if tag['Key'] == 'Name':
                        current_tables.add(tag['Value'].lower())

        return list(required_tables - current_tables)
    
    def inet_gateway_exists(self):

        print("Confirming internet gateway exists...")

        # get vpc id
        vpc_id = self.helpers.get_non_default_vpc_id(self.ec2)

        # retrieve internet gateways attached to this vpc
        if vpc_id:
            try:
                response = self.client.describe_internet_gateways(
                    Filters=[
                        {
                            'Name': 'attachment.vpc-id',
                            'Values': [vpc_id]
                        },
                    ]
                )
            except ClientError as e:
                print(e)
                exit(1)

            # if the gateway exists return true
            if response.get('InternetGateways'): # null check
                inet_gateway_id = response.get('InternetGateways')[0].get('InternetGatewayId')
                if inet_gateway_id:
                    return True
        
        return False

    def nat_gateway_exists(self):

        print("Confirming nat gateway exists...")
        
        # get vpc id
        vpc_id = self.helpers.get_non_default_vpc_id(self.ec2)

        #retrieve nat gateways attached to this vpc
        if vpc_id: # null check
            try:
                response = self.client.describe_nat_gateways(
                    Filters=[
                        {
                            'Name': 'vpc-id',
                            'Values': [vpc_id]
                        },
                    ]
                )
            except ClientError as e:
                print(e)
                exit(1)
    
            # if the gateway exists, set the checker to true
            if response.get('NatGateways'): # null check
                nat_gateway_id = response.get('NatGateways')[0].get('NatGatewayId')
                if nat_gateway_id:
                    return True
            
        return False
    
    def return_data(self):

        # call all methods and return data
        missing_security_groups = self.get_missing_security_groups()
        expected_subnets, missing_subnets = self.get_missing_subnets()
        missing_route_tables = self.get_missing_route_tables()
        inet_gateway = self.inet_gateway_exists()
        nat_gateway = self.nat_gateway_exists()
        vpc_exists = self.vpc_exists()

        inner_struct = {'MissingSecurityGroups': missing_security_groups, 'ExpectedSubnets':expected_subnets, 'MissingSubnets': missing_subnets, 'MissingRouteTables': missing_route_tables, 'NonDefaultVPCExists': vpc_exists, 
        'InternetGateway': inet_gateway, 'NatGateway': nat_gateway}
        outer_struct = {'VPC': inner_struct}
        print("outer_struct = {}".format(outer_struct))
        return outer_struct