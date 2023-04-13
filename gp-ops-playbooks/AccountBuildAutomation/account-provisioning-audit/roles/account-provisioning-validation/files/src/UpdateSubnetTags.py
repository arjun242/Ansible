import boto3
import sys

#########################################################################################
#
# A script to add a 'Type' tag to subnets.
# Subnet types: Database, Integration, External, Reach Back, Application, Endpoint
# E.g., {'Key': 'SubnetType', 'Value': 'database'}
# Usage: python UpdateSubnetTags.py <profile name>
#
#########################################################################################


class UpdateSubnetTags:

    if __name__ == '__main__':

        # check arguments
        if len(sys.argv) != 2:
            print("Usage: python Runner.py <profile_name>")
            exit(1)
        
        
        # variables
        user = sys.argv[1]
        session = boto3.session.Session(profile_name=user)
        ec2 = session.resource('ec2')
        account_id = session.client('sts').get_caller_identity().get('Account')
        print('Tagging Account: {0}\n'.format(account_id))

        # get all subnets
        subnets = list(ec2.subnets.all())

        # loop through subnets; get subnet name from tags; add type tag according to name
        for subnet in subnets:
            
            # get subnet resouce id
            resource_id = subnet.id

            if subnet.tags: # null check
    
                    for i in range(len(subnet.tags)):

                        key = subnet.tags[i]['Key']
                        value = subnet.tags[i]['Value']

                        try:
                            if (key == 'Name' and 'app' in value.lower()) or (key == 'Name' and 'application' in value.lower()):
                                print("Tagging Subnet ID: {0}\nName: {1}\nType: Application\n".format(resource_id, value))
                                ec2.create_tags(Resources=[resource_id], Tags=[{'Key': 'SubnetType', 'Value': 'application'}])
                                
                            elif (key == 'Name' and 'db' in value.lower()) or (key == 'Name' and 'database' in value.lower()):
                                print("Tagging Subnet ID: {0}\nName: {1}\nType: Database\n".format(resource_id, value))
                                ec2.create_tags(Resources=[resource_id], Tags=[{'Key': 'SubnetType', 'Value': 'database'}])

                            elif (key == 'Name' and 'rb' in value.lower()) or (key == 'Name' and 'reachback' in value.lower()):
                                print("Tagging Subnet ID: {0}\nName: {1}\nType: Reach Back\n".format(resource_id, value))
                                ec2.create_tags(Resources=[resource_id], Tags=[{'Key': 'SubnetType', 'Value': 'reachback'}])

                            elif (key == 'Name' and 'igr' in value.lower()) or (key == 'Name' and 'integration' in value.lower()):
                                print("Tagging Subnet ID: {0}\nName: {1}\nType: Integration\n".format(resource_id, value))
                                ec2.create_tags(Resources=[resource_id], Tags=[{'Key': 'SubnetType', 'Value': 'integration'}])

                            elif (key == 'Name' and 'ext' in value.lower()) or (key == 'Name' and 'external' in value.lower()):
                                print("Tagging Subnet ID: {0}\nName: {1}\nType: External\n".format(resource_id, value))
                                ec2.create_tags(Resources=[resource_id], Tags=[{'Key': 'SubnetType', 'Value': 'external'}])

                            elif (key == 'Name' and 'ep' in value.lower()) or (key == 'Name' and 'endpoint' in value.lower()):
                                print("Tagging Subnet ID: {0}\nName: {1}\nType: Endpoint\n".format(resource_id, value))
                                ec2.create_tags(Resources=[resource_id], Tags=[{'Key': 'SubnetType', 'Value': 'endpoint'}])
                        
                        except:
                            print("Error processing tag: {0} : {1}".format(key, value))
        