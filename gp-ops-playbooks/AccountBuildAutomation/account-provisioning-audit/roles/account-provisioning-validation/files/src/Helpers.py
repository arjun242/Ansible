import boto3

class Helpers:

    """
    Class that contains helper methods useful for several classes:
    This includes:
    Getting 'NextTokens' and 'NextMarkers' for looping through API responses with multiple pages
    Getting non-default VPC
    
    """

    # this method takes ec2 service resource, not ec2 client
    def get_non_default_vpc_id(self, ec2):

        # find non default vpc and return its id
        try:
            vpcs = ec2.vpcs.all()
        except ClientError as e:
            print(e)
            exit(1)
            
        vpc_id = None
        for vpc in vpcs:
            # check for non-default and uai tag
            if not vpc.is_default:
                uai_tag1 = {'Key': 'uai', 'Value': 'uai3033130'}
                uai_tag2 = {'Key': 'uai', 'Value': 'UAI3033130'}
                if vpc.tags and (uai_tag1 in vpc.tags or uai_tag2 in vpc.tags):
                    vpc_id = vpc.id
                    break

        return vpc_id

    def next_token(self, response):

        # needed for looping through response pages
        if 'NextToken' in response:
            return response['NextToken']
        else:
            return None

    def next_marker(self, response):

        # ditto 
        if 'NextMarker' in response:
            return response['NextMarker']
        else:
            return None
    
    def marker(self, response):
        # ditto 
        if 'Marker' in response:
            return response['Marker']
        else:
            return None

    