import boto3
import json
from Helpers import Helpers
from botocore.exceptions import ClientError

class SSMAuditer:

    """
    Class that performs Audit of System Manager configuration
    This includes:
    Correct documents exist
    Correct associations exist and are executing 
    Correct maintenance windows exist
    
    """

    def __init__(self, session, ideal_config):
        self.session = session
        self.ideal_config = ideal_config
        self.region = self.session.region_name
        self.ssm = self.session.client('ssm')
        self.ec2 = self.session.resource('ec2')
        self.helpers = Helpers()

    def get_missing_documents(self):

        print("Confirming required SSM documents exist...")
        
        # required shared documents
        required_documents = set(document.lower() for document in self.ideal_config['requiredDocuments']) # get security group names in lower case
   
        # get ssm documents 
        current_documents = set()
        try:
            response = self.ssm.list_documents(
                Filters =[
                    {
                        'Key': 'Owner',
                        'Values': ['Private']
                    },
                ],
                MaxResults=50,
            )
        except ClientError as e:
            print(e)
            exit(1)

        if response['DocumentIdentifiers']: # null check
            for i in range(len(response['DocumentIdentifiers'])):
                full_document_arn = response['DocumentIdentifiers'][i]["Name"].lower()

                # only consider ssm documents with proper format
                if 'arn:aws:ssm' in full_document_arn and 'document/' in full_document_arn: 
                    # print("properly formatted guardrails ssm doc found: {}".format(full_document_arn))
                    document_name = full_document_arn.split('document/')[1]
                    current_documents.add(document_name)
                # else:
                    # print("ignoring the following document: {}".format(full_document_arn))

        # if multiple pages exist then loop through them
        NextToken = self.helpers.next_token(response)
        while NextToken:
            try:
                response = self.ssm.list_documents(Filters =[{'Key': 'Owner','Values': ['Private']},], MaxResults=50, NextToken=NextToken)
            except ClientError as e:
                print(e)
                exit(1)

            for i in range(len(response['DocumentIdentifiers'])):
                full_document_arn = response['DocumentIdentifiers'][i]["Name"].lower()
                
                 # only consider ssm documents with proper format
                if 'arn:aws:ssm' in full_document_arn and 'document/' in full_document_arn: 
                    print("properly formatted guardrails ssm doc found: {}".format(full_document_arn))
                    document_name = full_document_arn.split('document/')[1]
                    current_documents.add(document_name)
                else:
                    print("ignoring the following document: {}".format(full_document_arn))

            NextToken = self.helpers.next_token(response)

        # return missing documents
        return list(required_documents - current_documents)

    def get_erroroneous_assocations(self):
        
        # create placeholder for required assocations
        required_associations = []

        # traverse through document that we need to generate assocations for
        for document in self.ideal_config['requiredAssocationDocuments']:

            # traverse through set of required assocation documents, build assocations objects
            required_associations.append(
                {
                    'key': 'Name',
                    'value': 'arn:aws:ssm:' + self.region + ':325381443140:document/{}'.format(document)
                }
            )

        erroneous_associations = dict()

        # check if assocations are missing or failed to execute
        for association in required_associations:
            try:
                response = self.ssm.list_associations(AssociationFilterList=[association])
            except ClientError as e:
                print(e)
                exit(1)
            try:
                status = response['Associations'][0]['Overview']['Status']
                if status == 'Failed':
                    erroneous_associations[association['value']] = status

            except:
                erroneous_associations[association['value']] = 'Missing'

        return erroneous_associations

    
    def get_maintenance_windows_status(self):

        print("Confirming maintenance windows status...")

        # get maintenance windows according to this filter
        required_windows = self.ideal_config['requiredWindows']
        try:
            response = self.ssm.describe_maintenance_windows(
                Filters=[
                    {
                        'Key': 'Name',
                        'Values': required_windows
                    },
                ],
            )
        except ClientError as e:
            print(e)
            exit(1)
            
        # get window status and return
        window_status = {'Prd-gp-standard-patching-window': 'Missing', 'NonPrd-gp-standard-patching-window': 'Missing'}
        if response['WindowIdentities']: # null check
            for window in required_windows:
                for i in range(len(response['WindowIdentities'])):
                    if response['WindowIdentities'][i]['Name'] == window and response['WindowIdentities'][i]['Enabled'] == True:
                        window_status[window] = 'Enabled'
                    elif response['WindowIdentities'][i]['Name'] == window and response['WindowIdentities'][i]['Enabled'] == False:
                        window_status[window] = 'Disabled'
        
        return window_status

    def get_erroneous_ssm_parameters(self):

        print("Confirming correct SSM parameters exist...")

        # required parameters
        required_parameters = self.ideal_config['requiredSSMParameters']

        # setup data struct to store results
        erroneous_parameters = {}

        # pull out parameters one by one
        for param in required_parameters:
            try:
                response = self.ssm.get_parameter(Name=param)

            #case where parameter is missing
            except self.ssm.exceptions.ParameterNotFound:
                erroneous_parameters[param] = 'Missing'
                continue
            except ClientError as e:
                print(e)
                exit(1)
        
            # cast where parameter exists - need to check value 
            current_value = response['Parameter']['Value']

            # these parameters need to be updated manually
            if param == '/automation/ami/centos7' or param == '/automation/ami/windows' or param == '/automation/ami/sg' or param == '/automation/domainJoinPassword' or param == '/automation/domainJoinUserName' or param == '/automation/win/NetGroup':
                if current_value == 'Update Manully' or current_value == 'nil': # this is not a typo - the default value for these SSM parameters is spelled 'Update Manully'
                    erroneous_parameters[param] = 'Incorrect'
            
            # the rest have specific default values
            elif param == '/automation/ami/base-key':
                if current_value != 'gp-base-key':
                    erroneous_parameters[param] = 'Incorrect'

            elif param == '/automation/ami/bucket':
                if current_value != 'gp-us-east-ops-automation-common-tools':
                    erroneous_parameters[param] = 'Incorrect'

            #elif param == '/automation/domainJoinUserName':
            #    if current_value != 'mgmt.cloud.ds.ge.com\\' + '\lg397053sv':
            #        erroneous_parameters[param] = 'Incorrect'
    
            elif param == '/automation/qualys/activationid':
                if current_value != '346faac7-8411-41aa-a235-105652a8064b':
                    erroneous_parameters[param] = 'Incorrect'
            
            elif param == '/automation/qualys/customerid':
                if current_value != '9c0e25de-0221-5af6-e040-10ac13043f6a':
                    erroneous_parameters[param] = 'Incorrect'
            
            #elif param == '/automation/win/NetGroup':
            #    if current_value != 'SVR_TCS_NIMBUS_2018_ADMIN , SVR_GE009000000_PWT_Migration_Factory':
            #        erroneous_parameters[param] = 'Incorrect'
            
            elif param == '/automation/ami/splunkpasskey':
                if current_value != 'pass4SymmKey = D85A9TuK8itcU^HA#04Wi7quVL4F#4':
                    erroneous_parameters[param] = 'Incorrect'
        
        # return param struct
        return erroneous_parameters
        
    def return_data(self):

        # call all methods and return data
        missing_documents = self.get_missing_documents()
        maintenance_windows_status = self.get_maintenance_windows_status()
        erroneous_associations = self.get_erroroneous_assocations()
        erroneous_parameters = self.get_erroneous_ssm_parameters()
        inner_struct = {'MissingDocuments': missing_documents, 'MaintenanceWindowStatus': maintenance_windows_status, 'ErroneousAssociations': erroneous_associations, 'ErroneousSSMParameters': erroneous_parameters}
        outer_struct = {'SSM': inner_struct}
        return outer_struct

    