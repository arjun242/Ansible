import boto3
import json

class IAMAuditer:

    """
    Class that performs Audit of Identity and Access Management
    This includes:
    Confirm required roles exist
    Confirm required policies exist

    """

    def __init__(self, session, ideal_config):
        self.session = session
        self.ideal_config = ideal_config
        self.iam = self.session.resource('iam')
        

    def get_missing_roles(self):

        print("Confirming required roles exist...")

        # get role names in the account
        try:
            role_list = self.iam.roles.all()
        except ClientError as e:
            print(e)
            exit(1)

        role_names = [role.name.lower() for role in role_list] 
        required_roles = self.ideal_config['requiredRoles']
        missing_roles = []

        # check role names against required roles
        for role in required_roles: 
            if role.lower() not in role_names:
                missing_roles.append(role)
        
        return missing_roles 
        
    def get_missing_policies(self):
    
        print("Confirming required policies exist...")

        # get policy names in the account
        try:
            current_policies = self.iam.policies.all()
        except ClientError as e:
            print(e)
            exit(1)
            
        policy_names = [policy.policy_name.lower() for policy in current_policies]
        required_policies = self.ideal_config['requiredPolicies']
        missing_policies = []

        # check policy names against required policies
        for policy in required_policies:
            if policy not in policy_names:
                missing_policies.append(policy)
        
        return missing_policies
    
    def return_data(self):

        # call all methods and return data
        missing_roles = self.get_missing_roles()
        missing_policies = self.get_missing_policies()
        inner_struct = {'MissingRoles': missing_roles, 'MissingPolicies': missing_policies}
        outer_struct = {'IAM': inner_struct}
        return outer_struct