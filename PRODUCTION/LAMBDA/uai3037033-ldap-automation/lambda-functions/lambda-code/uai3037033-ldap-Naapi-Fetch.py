import json
import boto3
import requests
import base64
import logging 
import os
from botocore.exceptions import ClientError
logger = logging.getLogger() 
logger.setLevel(logging.INFO) 
#fetch API_KEY stored in secrets manager
def get_secret():
    logger.info("Inside get_secret...")
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
#fetch AccountID detailes from NAAPI api by passing API_KEY(stored in secrets manager) and return accumulated_items 
def naapi_fetch(accountID):
    logger.info('inside the naapi_fetch function')
    try:
        secretValues = json.loads(get_secret())
        naapi_api_key=secretValues['api_key']
        headers = {"x-api-key": naapi_api_key,"Content-Type": "application/json"}
        AccountIds = accountID.split(',')
        responses=[]
        for account in AccountIds:
            AccountId=int(account)
            if len(account) ==12:
                base_url = os.environ['base_url']+'size=1000'
                payload = {"awsAccountId":AccountId}
                response = requests.get(base_url,headers=headers,params=payload,verify=True)
                responses.append(response.json().get('hits').get('hits'))            
            else:
                responses.append('incorrect')
        return responses
    except Exception as e:
        return f"Exception occured while fetching instance detailes from NAAPI API,exception is: {e}"
#parse JSON data ,to populate dynamodb        
def json_parser_ddb(sub_list):
    try:
        logger.info('inside json_parser_ddb function')
        items=[]
        if len(sub_list) >0 :
            for i in range(len(sub_list)):
                item={}
                item["awsAccountId"]= sub_list[i]['_source']['awsAccountId']            
                if sub_list[i]['_source']['Tags'].get('uai'):
                	item["uai"] = sub_list[i]['_source']['Tags']['uai']
                else:
                	item["uai"] = 'NA'
                if sub_list[i]['_source']['Tags'].get('appname'):
                	item["AppName"] = sub_list[i]['_source']['Tags']['appname']
                else:
                	item["AppName"] = ''
                item["NetGroupName"]= ""
                item["instanceID"]= sub_list[i]['_source']['configuration']['instanceId']
                if sub_list[i]['_source']['Tags'].get('env'):
                	item["Env"]= sub_list[i]['_source']['Tags']['env']
                else:
                	item["Env"]= ""
                if sub_list[i]['_source']['Tags'].get('role'):
                	item["Purpose/role"]= sub_list[i]['_source']['Tags']['role']
                else:
                	item["Purpose/role"]=""
                item["PrivateIp"]= sub_list[i]['_source']['configuration']['privateIpAddress']
                item["ExistingNetGroups"]= ""
                item["Connectivity"]= ""
                item["LdapStatus"]=""
                exclude_factors=[sub_list[i]['_source']['Tags'].get('os-family'),sub_list[i]['_source']['Tags'].get('Name'),sub_list[i]['_source']['Tags'].get('role'),item["uai"]]
                #Exclude these values from populating Dynamodb table ..,when uai is not defined and crashed instance i-0c8e4366e278dda8b and bastion,NAT instances
                exclude_values=os.environ['exclude_values'].split(',')
                if all(x not in exclude_factors for x in exclude_values):
                    items.append(json.dumps(item))                          
        else:
            for k in range(len(sub_list)):
                awsAccountId= sub_list[k]['_source']['awsAccountId']
                logger.info('No instances in accountID: ',awsAccountId)           
        return items       
    except Exception as e:
        return f"Exception occured while parsing JSON data,exception is: {e}"
#send json data to SQS queue after parsing       
def send_to_sqs(accountID):
    try:
        logger.info('inside get_acc_info function')
        naapi_result=naapi_fetch(accountID)
        logger.info(f'Naapi Result is: {naapi_result}')
        
        #fetch single_id from naapi_fetch with accountIDs, filter Invalid results and parse it
        if not isinstance(naapi_result,str):
            accumulated_items=[]
            for s_id in naapi_result:
                if s_id != None and s_id != 'incorrect':
                    accumulated_items.append(json_parser_ddb(s_id))
                else:
                    accumulated_items.append(s_id)
            #send one accound_id detailes as single message to sqs_queue 
            client = boto3.client('sqs')
            ret_values={}
            for k,account in zip(range(len(accumulated_items)),accountID.split(',')):
                if accumulated_items[k] != None and len(accumulated_items[k])>0 and accumulated_items[k] != 'incorrect':
                    try:
                        logger.info(f'length of each batch_to_SQS: {len(accumulated_items[k])}')
                        logger.info(f'Content of batch_to_SQS are: {accumulated_items[k]}')
                        response = client.send_message(
                            QueueUrl = os.environ['QueueUrl'],
                            MessageBody = json.dumps(accumulated_items[k]))
                        ret_values[account]= f'Successfully sent {len(accumulated_items[k])} instances to SQS Queue'
                    except Exception as e:
                        ret_values[account]=f'lambda unable to push message to SQS Queue Due to Network issues'
                elif accumulated_items[k] == 'incorrect':
                    ret_values[account]='Incorrect AccountID(length != 12)'
                elif accumulated_items[k] != None and len(accumulated_items[k])==0:
                    ret_values[account]='Zero instances AccountID'
                else:
                    ret_values[account]='Invalid AccountID'
            return {
                'statusCode': 200,
                'body': json.dumps(ret_values)
            }
        else:
            return {
                'statusCode': 200,
                'body': naapi_result
            }
    
    except Exception as e:
        return {
                'statusCode': 200,
                'body': json.dumps(ret_values)
            }
#takes accountID from  postman then parse and process it
def lambda_handler(event, context):
    logger.info("Inside lambda_handler...")
    accountID=event['body']
    sqs_out=send_to_sqs(accountID) 
    return sqs_out