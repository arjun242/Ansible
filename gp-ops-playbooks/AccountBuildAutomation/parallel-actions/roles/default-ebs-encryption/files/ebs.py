#Script to enable default EBS Encryption
import boto3
ec2_client = boto3.client('ec2',aws_access_key_id="{{access_key}}",
    aws_secret_access_key="{{secret_key}}",
    aws_session_token="{{session_token}}",region_name="{{aws_region}}")

ec2_client.modify_ebs_default_kms_key_id(KmsKeyId='alias/common-kms-key')
ec2_client.enable_ebs_encryption_by_default()
