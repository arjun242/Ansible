import boto3
client = boto3.client('codestar-connections',aws_access_key_id="{{access_key}}",
    aws_secret_access_key="{{secret_key}}",
    aws_session_token="{{session_token}}",region_name="{{aws_region}}")
response = client.create_host(
    Name='github-build-ge',
    ProviderType='GitHubEnterpriseServer',
    ProviderEndpoint='https://github.build.ge.com/',
    VpcConfiguration={
        'VpcId': '{{codestar_vpc_id}}',
        'SubnetIds': [
            '{{codestar_subnet1}}',
            '{{codestar_subnet2}}',
        ],
        'SecurityGroupIds': [
            '{{codestar_sgID}}',
        ]
    },
    Tags=[
        {
            'Key': 'Name',
            'Value': 'github-build-ge'
        },
    ]
)
print(response)