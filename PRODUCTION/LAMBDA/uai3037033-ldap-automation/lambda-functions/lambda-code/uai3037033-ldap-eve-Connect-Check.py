import json
import os
import requests
import urllib3
import boto3
import time
import base64
import logging
from time import sleep
from botocore.exceptions import ClientError
logger = logging.getLogger() 
logger.setLevel(logging.INFO) 
#Fetch ansible tower api-key from secrets manager
def get_secret():
    logger.info("Inside get_secret...")
    #calling variables from Environment Variables
    secret_name = os.environ['secret_name']
    region_name = os.environ['region_name']
    session = boto3.session.Session()
    client = session.client( service_name='secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
        else:
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            logger.info("Inside string response...")
            return get_secret_value_response['SecretString']
        else:
            logger.info("Inside binary response...")
            return base64.b64decode(get_secret_value_response['SecretBinary']) 
#fetching JobId from jobtemplate name
def JT_id(towerUrl,jt_name,headers):
    url = towerUrl + '?search='+jt_name
    urllib3.disable_warnings()
    resp = requests.request("GET",url, headers=headers, verify=False)
    if resp.status_code == 200:
        response_json = resp.json()
        return response_json['results'][0]['id']
    else:
        return -1
def assumeRole(account_number):
    sts_connection = boto3.client('sts')

    # #Assume the role in the other account
    acct_b = sts_connection.assume_role(
        RoleArn="arn:aws:iam::" + account_number + ":role/app/uai3037033-ldap-lambda-assume-role",
        RoleSessionName="cross_acct_lambda"
    )
    return acct_b
#waiting for ec2 instance status checks 2/2 passed,waits for Max.10mins
def wait_for_statuschecks(instanceId,ec2_region,ACCESS_KEY,SECRET_KEY,SESSION_TOKEN):
    client = boto3.client('ec2',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,aws_session_token=SESSION_TOKEN,region_name=ec2_region)
    waiter_instance = client.get_waiter('instance_status_ok')
    waiter_system = client.get_waiter('system_status_ok')
    waiter_instance.wait(InstanceIds=[instanceId])
    waiter_system.wait(InstanceIds=[instanceId])
#To call Ansible tower api
def tower_api(job_id,limit_address,towerUrl,headers):
    data = {"limit": limit_address}
    url = f'{towerUrl}/{job_id}/launch/'
    urllib3.disable_warnings()
    response = requests.request("POST",url, headers=headers, json=data, allow_redirects=False, verify=False)
    return response
def runSSMDocument(docName,ec2_region,instanceId,ACCESS_KEY,SECRET_KEY,SESSION_TOKEN):
    
    client = boto3.client('ssm',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, aws_session_token=SESSION_TOKEN,region_name=ec2_region)
    ids = []
    ids.append(instanceId)     
    resp = client.send_command(InstanceIds = ids,DocumentName=docName)
    command_id = resp['Command']['CommandId']
    if resp['Command']['Status'] == 'Success':
        logger.info('SSM Doc execution complete')
        return True
    else:
        sleep(5)
        output = client.get_command_invocation(CommandId=command_id, InstanceId=ids[0])
        logger.info(output['Status'])
        while(output['Status'] == 'Pending' or output['Status'] == 'InProgress'):
            sleep(15)
            output = client.get_command_invocation(CommandId=command_id, InstanceId=ids[0])
            logger.info(output['Status'])
        if output['Status'] == 'Success':
            return True
        return False
        
#update dynamodb table and trigger tower API
def lambda_handler(event, context):
    logger.info(json.dumps(event))
    dynamo_resource = boto3.resource('dynamodb')
    table = dynamo_resource.Table(os.environ['ddb_table'])
    event_modify=json.loads(event["Records"][0]["body"])
    logger.info(event_modify)
    try:
        item={}
        tags=event_modify["detail"]["requestParameters"]['tagSpecificationSet']['items'][0]['tags']
        for tag in tags:
            if tag['key'] == 'uai':
                item['uai'] = tag['value']
            if tag['key'] == 'appname':
                item['AppName']= tag['value']
            if tag['key'] == "role":
                item["Purpose/role"]=tag['value']
            if tag['key'] == "env":
                item["Env"]=tag['value']
            if tag['key'] == "os-family":
                os_family=tag['value']
            else:
                os_family=''
        instanceId =event_modify["detail"]["responseElements"]["instancesSet"]["items"][0]["instanceId"]
        item["instanceID"]=instanceId
        item["PrivateIp"]=event_modify["detail"]["responseElements"]["instancesSet"]["items"][0]["privateIpAddress"]
        item["NetGroupName"]=''
        item["Connectivity"]=''
        item["ExistingNetGroups"]= ""
        item["LdapStatus"]=""
        item["awsAccountId"]=event_modify["detail"]["userIdentity"]["accountId"]
        account_number=event_modify["detail"]["userIdentity"]["accountId"]
        ec2_region=event_modify['region']
        private_ip= event_modify["detail"]["responseElements"]["instancesSet"]["items"][0]["privateIpAddress"]
        #if os-family belongs to windows, exclude that instance for Dynamodb and LDAP installation
        logger.info(instanceId)
        if os_family != 'windows':
            table.put_item(Item=item)
            #Assume remote account ec2 and ssm permissions
            acct_b = assumeRole(account_number)
            ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
            SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
            SESSION_TOKEN = acct_b['Credentials']['SessionToken']
            #Make Lambda function wait for status checks successful
            logger.info('waiting for ec2 instance status checks 2/2 passed,waits for Max.10mins')
            waiting=wait_for_statuschecks(instanceId,ec2_region,ACCESS_KEY,SECRET_KEY,SESSION_TOKEN)
            #run SSM document, to configure ansible user
            docName="arn:aws:ssm:"+ ec2_region +":325381443140:document/app-ansibleUser-publicKey"
            logger.info(docName)
            run_ssm=runSSMDocument(docName,ec2_region,instanceId,ACCESS_KEY,SECRET_KEY,SESSION_TOKEN)
            if run_ssm:
                logger.info(f'SSMDocument successfully ran on instanceID: {instanceId} in accountID: {account_number}')
            else:
                logger.info(f'SSMDocument Failed to run on instanceID: {instanceId} in accountID: {account_number}')
            #######
            secretValues = json.loads(get_secret())
            oauth2_token_value=secretValues['Ansibleoauth2Tokenvalue']  # your token value from Tower
            towerUrl=os.environ['tower_url']
            headers = {'Authorization': 'Bearer ' + oauth2_token_value}
            event_jt_name=os.environ['jt_name']                      #fetched from envionment variable
            con_jobid= JT_id(towerUrl,event_jt_name,headers)
            if con_jobid!=-1:
                logger.info('calling connectivity and LDAP playbook')
                invoke_ldap_pb=tower_api(con_jobid,private_ip,towerUrl,headers)
                logger.info(f'response is: {invoke_ldap_pb}') 
            else:
                logger.info(f"job template {netgrp_jt_name} doesn't exists")
        else:
            logger.info(f"Newly launched instnace not belongs to LINUX family, LDAP can't installed")
    except Exception as e:
        logger.info(f"Exception occured,exception is: {e}")