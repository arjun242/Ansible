import json
import requests
import urllib3
import boto3
import base64
import itertools
import logging
import os
from botocore.exceptions import ClientError
logger = logging.getLogger() 
logger.setLevel(logging.INFO)

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

#To call Ansible tower api
def tower_api(job_id,limit_address,towerUrl,headers):
    try:        
        url = f'{towerUrl}/{job_id}/launch/'              
        data = {"limit": limit_address}
        response = requests.request("POST",url, headers=headers, json=data, allow_redirects=False, verify=False)
        return response
    except Exception as e:
        return f'exception occured while invoking ansible tower api, Exception is: {e}'
        
#lambda triggered by SQS queue
def lambda_handler(event, context):
    try:
        logger.info('Json data received fom SQS Queue successfully')
        logger.info(json.dumps(event))
        #initialize dynamodb resource with boto3
        dynamo_resource = boto3.resource('dynamodb')
        table = dynamo_resource.Table(os.environ['ddb_table'])
        #Capture SQS event from lambda1&SQS queue, then parse it
        single_acc_id = json.loads(event['Records'][0]['body'])
        #gather all ip-address from sqs event and store in list
        ip_address = [] 
        #gather all connectivity status from sqs event and store in list  
        con_status = []   
        #loop through single account and update dynamodb table with instance detailes 
        for single_instance in single_acc_id:
            single_instance_dict=json.loads(single_instance)
            table.put_item(Item=single_instance_dict)
            ip_address.append(single_instance_dict['PrivateIp'])
            con_status.append(single_instance_dict["Connectivity"])
        logger.info('DynamoDB table populated successfully')
        #define limit ip address for ansible playbook
        limit_address= ','.join(ip_address)
        #Filter instances based on connectivity status and group it
        instances_without_connectivity =[]
        instances_with_connectivity=[]
        for ip,connect in zip(ip_address,con_status):
            if not connect:
                instances_without_connectivity.append(ip)
            elif connect:
                instances_with_connectivity.append(ip)
        limit_addr_connect= ','.join(instances_without_connectivity)
        limit_addr_ldap= ','.join(instances_with_connectivity)
    except Exception as e:
        logger.info(f'Exception occured while captuing sqs event and pushing it into Dynamodb table,exception is: {e}')
    #to trigger Ansible tower api 
    try:
        secretValues = json.loads(get_secret())
        oauth2_token_value=secretValues['Ansibleoauth2Tokenvalue']  # your token value from Tower
        towerUrl=os.environ['tower_url'] 
        headers = {'Authorization': 'Bearer ' + oauth2_token_value}
        #if connectivity is not there ,trigger connectivity playbook
        if instances_without_connectivity:            
            conn_jt_name=os.environ['conn_jt_name']
            id_con=JT_id(towerUrl,conn_jt_name,headers)
            if id_con != -1:
                logger.info('calling connectivity playbook')
                invoke_conn_pb=tower_api(id_con,limit_addr_connect,towerUrl,headers)
                logger.info(f'response is: {invoke_conn_pb}')
            else:
                logger.info(f"job template {conn_jt_name} doesn't exists")
        #if connectivity is there ,trigger LDAP playbook  
        elif instances_with_connectivity:
            ldap_jt_name=os.environ['ldap_jt_name']
            id_ldap=JT_id(towerUrl,ldap_jt_name,headers)
            if id_ldap != -1:
                logger.info('calling LDAP playbook')
                invoke_ldap_pb=tower_api(id_ldap,limit_addr_ldap,towerUrl,headers)
                logger.info(f'response is: {invoke_ldap_pb}')
            else:
                logger.info(f"job template {ldap_jt_name} doesn't exists")
    except Exception as e:
        logger.info(f'Exception occured while calling ansible tower API(inside lambda function),exception is: {e}')
        

    