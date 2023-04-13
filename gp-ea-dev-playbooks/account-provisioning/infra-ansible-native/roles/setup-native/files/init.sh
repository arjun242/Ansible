#!/bin/bash

# Initialize new accounts
#  1. Get credentials for bu-iam-admin
#  2. use CLI to create user with IAM and cloudformation full
#  3. get certenditals
#  4. use stack master with new account to create SAAdmin Role.


#Getting credentials for bu-iam-admin
pfile=$1
user=$2
region=$3

#echo "Account Number: ${actnum}"
#cred=$(cat ~/.aws/credentials | grep ${actnum} | grep bu-iam-admin | cut -c2- | rev | cut -c2- | rev)
#echo "Profile Name: ${cred} "
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
#echo "Region is: ${region}"

echo "Create local user"
aws iam create-user --user-name $user --profile $pfile --region $region
aws iam create-group --group-name temp-acct-init --profile $pfile --region $region 
aws iam add-user-to-group --group-name temp-acct-init --user-name $user --profile $pfile --region $region 

aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/IAMFullAccess --group-name temp-acct-init --profile $pfile --region $region
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/AWSCloudFormationFullAccess --group-name temp-acct-init --profile $pfile --region $region

echo "getting key for new user"
credsjson=$(aws iam create-access-key --user-name $user --profile $pfile --region $region)
key=$(echo $credsjson | jq -r .AccessKey.AccessKeyId)
secret=$(echo $credsjson | jq -r .AccessKey.SecretAccessKey)

echo "set key for user"
export AWS_ACCESS_KEY_ID=$key
export AWS_SECRET_ACCESS_KEY=$secret 
echo $credsjson 
echo "AWS_ACCESS_KEY_ID=$key" 
echo "AWS_SECRET_ACCESS_KEY=$secret" 
echo "sleep for a few"
sleep 10
#env

stackExist=$(aws cloudformation describe-stacks --stack-name gp-stackset-execution --query 'Stacks[*].[StackStatus]')
result=$?
#Stack does not exist create
if [ $result -ne 0 ]; then
  echo "create stack for execution role"
  aws cloudformation create-stack --stack-name gp-stackset-execution --template-body file://stackset-execution.yml --capabilities CAPABILITY_NAMED_IAM --output json --region $region

  aws cloudformation wait stack-create-complete --stack-name gp-stackset-execution --region $region
else
  aws cloudformation update-stack --stack-name gp-stackset-execution --template-body file://stackset-execution.yml --capabilities CAPABILITY_NAMED_IAM --output json --region $region

  aws cloudformation wait stack-update-complete --stack-name gp-stackset-execution --region $region
fi


echo "cleanup old user"
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY

aws iam detach-group-policy --group-name temp-acct-init --policy-arn arn:aws:iam::aws:policy/IAMFullAccess --profile $pfile --region $region
aws iam detach-group-policy --group-name temp-acct-init --policy-arn arn:aws:iam::aws:policy/AWSCloudFormationFullAccess --profile $pfile --region $region
aws iam remove-user-from-group --group-name temp-acct-init --user-name $user --profile $pfile --region $region
aws iam delete-group --group-name temp-acct-init --profile $pfile --region $region
aws iam delete-access-key --user-name $user --access-key-id $key --profile $pfile --region $region 

aws iam delete-user --user-name $user --profile $pfile --region $region




#538462866776
#100148143185
#372444449616