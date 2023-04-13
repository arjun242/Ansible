import boto3
import json

bucket_names_list  = ['gp-ops-ssm-logs','gp-us-east-ops-automation-common-artifacts','gp-us-east-ops-automation-common-tools','gp-eu-west-ops-automation-common-artifacts']
# bucket_names_list  = ['gp-ops-ssm-logs']
s3 = boto3.client('s3',aws_access_key_id="{{ops_access_key}}",
    aws_secret_access_key="{{ops_secret_key}}",
    aws_session_token="{{ops_session_token}}",
    region_name="us-east-1")

account_number = '{{ account_number }}'
# account_number = '935191336473'
arn_to_be_appended = 'arn:aws:iam::' + account_number + ':root'
i = 0
for bucket_name in bucket_names_list:
    bucket_policy = s3.get_bucket_policy(Bucket=bucket_name)
    temp = json.loads(bucket_policy['Policy'])

    statement_list = temp['Statement']
    for statement in statement_list:
        if statement['Sid'].split(' ')[0] == 'Ansible':
            statement['Principal']['AWS'].append(arn_to_be_appended)

    to_be_updated_json = json.dumps(temp)
    response = s3.put_bucket_policy(Bucket=bucket_name, Policy=to_be_updated_json)
    print(response)
    print('\n\n\n')
    i += 1