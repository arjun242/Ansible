import json
import os
import requests
import urllib3
import boto3
import time
import base64
import logging
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
        
#To call Ansible tower api
def tower_api(job_id,limit_address,ui_data,netgroup_name,towerUrl,headers):
    url = f'{towerUrl}/{job_id}/launch/'
    data = {'extra_vars': {netgroup_name: ui_data["NetGroupName"].strip()},"limit": limit_address}
    response = requests.request("POST",url, headers=headers, json=data, allow_redirects=False, verify=False)
    return response 
def lambda_handler(event, context):
    try:
        logger.info(event)
        dynamo_resource = boto3.resource('dynamodb')
        table = dynamo_resource.Table(os.environ['ddb_table'])
        ui_data = json.loads(event["Records"][0]["body"])
        instanceids=ui_data["instanceID"].split(',')
        if len(instanceids) > 1:
            netgroup_name="grouped_netgroup"
        else:
            netgroup_name="netgroup"
        grouped_ips=[]
        for instance in instanceids:
            res_get= table.get_item(Key={'uai': ui_data["uai"],'instanceID': instance})        
            Private_ip=res_get['Item']['PrivateIp']
            grouped_ips.append(Private_ip)
        grouped_ips_comma_sep=",".join(grouped_ips)
        secretValues = json.loads(get_secret())
        oauth2_token_value=secretValues['Ansibleoauth2Tokenvalue']  # your token value from Tower
        towerUrl=os.environ['tower_url']
        headers = {'Authorization': 'Bearer ' + oauth2_token_value}        
        if res_get['Item']['Connectivity'] =='OK':
            netgrp_jt_name=os.environ['netgrp_jt_name']
            netgrp_id=JT_id(towerUrl,netgrp_jt_name,headers)            
            if netgrp_id != -1:
                logger.info('calling dynamic netgroup addition playbook')
                invoke_custom_pb=tower_api(netgrp_id,grouped_ips_comma_sep,ui_data,netgroup_name,towerUrl,headers)
                logger.info(f'response is: {invoke_custom_pb}')
            else:
                logger.info(f"job template {netgrp_jt_name} doesn't exists")                
        elif res_get['Item']['Connectivity'] =='':
            conn_jt_name=os.environ["conn_jt_name"]
            connect_id=JT_id(towerUrl,conn_jt_name,headers)            
            if connect_id != -1:
                logger.info('calling connectivity and LDAP playbook')
                invoke_ldap_pb=tower_api(connect_id,grouped_ips_comma_sep,ui_data,netgroup_name,towerUrl,headers)
                logger.info(f'response is: {invoke_ldap_pb}')
            else:
                logger.info(f"job template {conn_jt_name} doesn't exists")

    except Exception as e:
        logger.info(f"Exception occured while triggering Ansible tower api,exception is: {e}")