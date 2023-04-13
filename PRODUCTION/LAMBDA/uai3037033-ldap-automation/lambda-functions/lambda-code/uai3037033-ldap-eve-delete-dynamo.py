import boto3
import json
import os
import logging
from boto3.dynamodb.conditions import Key, Attr
logger = logging.getLogger() 
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    delete_ddb_item=json.loads(event["Records"][0]["body"])
    dynamo_resource = boto3.resource('dynamodb')
    table = dynamo_resource.Table(os.environ['ddb_table'])
    instanceId =delete_ddb_item["detail"]["responseElements"]["instancesSet"]["items"][0]["instanceId"]
    logger.info(instanceId)
    try:        
        #Make Initial Scan
        response = table.scan()
        #Extract the Results
        items = response['Items']
        for item in items:
            if item['instanceID']==instanceId:
                table.delete_item(
                    Key={
                        'uai': item['uai'],
                        'instanceID': item['instanceID']
                    }
                )
    
        #pagination requires when DynamoDB table size exceeds 1MB
        while 'LastEvaluatedKey' in response:
            logger.info('checking pagination')
            key = response['LastEvaluatedKey']
            response = table.scan(ExclusiveStartKey=key)
            items = response['Items']
            for item in items:
                if items['instanceID']==instanceId:
                    table.delete_item(
                        Key={
                            'uai': item['uai'],
                            'instanceID': item['instanceID']
                        }
                    )
        logger.info(f"{instanceId} is removed from DynamoDb successfully")
    except Exception as e:
        logger.info(f"Exception occured while deleting terminated instance,exception is: {e}")