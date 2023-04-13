import boto3
import sys
from os import path


#########################################################################################
#
# Script to attach ssm-automation-managed-policy to instance profiles where missing
#
# Usage: python AttachProfilePolicy.py <aws profile name> <output file>
#
#########################################################################################


class AttachProfilePolicy:

    def get_profile_roles(client):
        
        # get all roles from instance profiles
        roles = set()
        response = client.list_instance_profiles()
        if response['InstanceProfiles']: #null check
            for i in range(len(response['InstanceProfiles'])):
                if response['InstanceProfiles'][i]['Roles']: # null check
                    roles.add(response['InstanceProfiles'][i]['Roles'][0]['RoleName'])

        # loop through all pages if they exist
        if 'Marker' in response:
            marker = get_marker(response)
            while marker:
                response = client.list_instance_profiles(Marker=marker)
                for i in range(len(response['InstanceProfiles'])):
                    if response['InstanceProfiles'][i]['Roles']: # null check
                        roles.add(response['InstanceProfiles'][i]['Roles'][0]['RoleName'])
                marker = get_marker(response)

        return roles

    def get_marker(response):

        if 'Marker' in response:
            return response['Marker']
        else:
            return None

    def filter_roles(client, roles, policy_arn):
        
        filtered_roles = set()
        check = True

        # loop through roles and identify those that already have this policy attached
        for role in roles:
            try:
                response = client.list_attached_role_policies(RoleName=role)
                if response['AttachedPolicies']: # null check
                    for i in range(len(response['AttachedPolicies'])):
                        match = response['AttachedPolicies'][i]['PolicyArn']
                        if match == policy_arn:
                            filtered_roles.add(role)
                            check = False 
                            break
                            
                
                # loop through all pages if multiple and if policy hasn't already been found
                if 'Marker' in response and check:
                    marker = get_marker(response)
                    while marker:
                        response = client.list_attached_role_policies(RoleName=role, Marker=marker)
                        if response['AttachedPolicies']: # null check
                            for i in range(len(response['AttachedPolicies'])):
                                match = response['AttachedPolicies'][i]['PolicyArn']
                                if match == policy_arn:
                                    filtered_roles.add(role)
                                    check = False 
                                    break
                                    
                        marker = get_marker(response)

            except (client.exceptions.NoSuchEntityException, client.exceptions.InvalidInputException, client.exceptions.ServiceFailureException) as e:
                print("Exception occured processing role: {0}".format(role))
                print(e)
        
        roles = roles - filtered_roles
        return roles, filtered_roles
        
    def attach_policy(client, roles, policy_arn):
        
        success_list = list()
        failed_list = list()

        # loop through all roles and attach policy
        for role in roles:
            try:
                response = client.attach_role_policy(RoleName=role, PolicyArn=policy_arn)
                success_list.append(role)
            except (client.exceptions.NoSuchEntityException, client.exceptions.LimitExceededException, client.exceptions.InvalidInputException, client.exceptions.UnmodifiableEntityException,
            client.exceptions.PolicyNotAttachableException, client.exceptions.ServiceFailureException) as e:

                failed_list.append(role)
                print("Exception occured processing role: {0}".format(role))
                print(e)

        return success_list, failed_list


    def write_results(success_list, failed_list, filtered_roles, account_id, filename):
        
        
        with open(filename, "w") as file:

            # write successful attachments
            file.write("Account: {0}\n\n".format(account_id))
            file.write("Successful policy attachments: {0}\n".format(len(success_list)))
            for profile in success_list:
                file.write(profile + "\n")
            
            # write failed attachments
            file.write("\nFailed policy attachments: {0}\n".format(len(failed_list)))
            for profile in failed_list:
                file.write(profile + "\n")

            # write roles already had policy attached
            file.write("\nPolicy already attached: {0}\n".format(len(filtered_roles)))
            for profile in filtered_roles:
                file.write(profile + "\n")


    if __name__ == '__main__':

        # check arguments
        if len(sys.argv) != 3:
            print("Usage: python Runner.py <profile_name> <output-filename")
            exit(1)
        
        # check if output file already exists
        elif path.exists(sys.argv[2]):
            print("Error: '{0}' already exists".format(sys.argv[2]))
            exit(1)

        # variables
        user = sys.argv[1]
        filename = sys.argv[2]
        session = boto3.session.Session(profile_name=user)
        client = session.client('iam')
        account_id = session.client('sts').get_caller_identity().get('Account')
        policy_arn = 'arn:aws:iam::' + account_id + ':policy/ssm-automation-managed-policy'

        # get all roles from instance profiles
        roles = get_profile_roles(client=client)

        # filter roles that already have the policy
        roles, filtered_roles = filter_roles(client=client, roles=roles, policy_arn=policy_arn)

        # attach policy
        success_list, failed_list = attach_policy(client=client, roles=roles, policy_arn=policy_arn)

        # write results
        write_results(success_list=success_list, failed_list=failed_list, filtered_roles=filtered_roles, account_id=account_id, filename=filename)

    