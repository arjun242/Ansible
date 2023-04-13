import boto3
import json
import string
import ast
from collections import defaultdict

client=boto3.client('ssm',
aws_access_key_id  = "{{ aws_access_key_id }}",
aws_secret_access_key = "{{ aws_secret_access_key }}",
aws_session_token = "{{ aws_session_token }}",
region_name= "{{ region_name }}")

def execute_doc():
     return client.start_automation_execution(
          DocumentName='share_existing_ssm_doc'
    
)
if __name__=="__main__":
    doc = execute_doc()
    print(doc)