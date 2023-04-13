#Script to request service quota increase for RDS
import boto3
client = boto3.client('service-quotas',aws_access_key_id="{{access_key}}",
    aws_secret_access_key="{{secret_key}}",
    aws_session_token="{{session_token}}",
    region_name="{{aws_region}}")

#Increase the quota limit of Option groups to 100
response = client.request_service_quota_increase(
    ServiceCode='rds',
    QuotaCode='L-9FA33840',
    DesiredValue=100
)

#Increase the quota limit of Parameter groups to 250
response1 = client.request_service_quota_increase(
    ServiceCode='rds',
    QuotaCode='L-DE55804A',
    DesiredValue=250
)
