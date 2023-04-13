import boto3
import json
import requests
import urllib3
import base64
import logging
import os
from botocore.exceptions import ClientError
logger = logging.getLogger() 
logger.setLevel(logging.INFO) 

#get Ansible tower api key from secrets manager
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
        
#lambda triggered by SQS event from connect_check ansible playbook
def lambda_handler(event, context):
    try:
        logger.info(json.dumps(event))
        #fetch ip-adresses of instances from SQS queue and execute playbook to install LDAP
        instances = event['Records'][0]['body'].strip('[]').split(',')
        limit_instances=[]
        for ip in instances:
            limit_instances.append(ip.replace(' ',''))
        limit_addr_ldap= ','.join(limit_instances)
        secretValues = json.loads(get_secret())
        oauth2_token_value=secretValues['Ansibleoauth2Tokenvalue']  # your token value from Tower
        towerUrl=os.environ['tower_url']
        headers = {'Authorization': 'Bearer ' + oauth2_token_value}
        ldap_jt_name=os.environ['ldap_jt_name']
        id_ldap=JT_id(towerUrl,ldap_jt_name,headers)
        if id_ldap != -1:
            logger.info('calling LDAP playbook')
            invoke_ldap_pb=tower_api(id_ldap,limit_addr_ldap,towerUrl,headers)
            logger.info(f'response is: {invoke_ldap_pb}')
        else:
            logger.info(f"job template {ldap_jt_name} doesn't exists")
        
    except Exception as e:
        logger.info(f"Exception occured while triggering tower API of LDAP playbook,inside lambda function,exception is: {e}")
