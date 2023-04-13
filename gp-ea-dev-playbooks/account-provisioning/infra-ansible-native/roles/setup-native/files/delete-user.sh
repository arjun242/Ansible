#! /bin/bash

actnum=$1
user=$2
region=$3
key=$4
echo "Account Number: ${actnum}"
#cred=$(cat ~/.aws/credentials | grep ${actnum} | grep bu-iam-admin | cut -c2- | rev | cut -c2- | rev)
cred="default"
echo "Profile Name: ${cred} "
#unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
echo "Region is: ${region}"

aws iam detach-group-policy --group-name temp-acct-init --policy-arn arn:aws:iam::aws:policy/IAMFullAccess --profile $cred --region $region
aws iam detach-group-policy --group-name temp-acct-init --policy-arn arn:aws:iam::aws:policy/AWSCloudFormationFullAccess --profile $cred --region $region
aws iam remove-user-from-group --group-name temp-acct-init --user-name $user --profile $cred --region $region
aws iam delete-group --group-name temp-acct-init --profile $cred --region $region
aws iam delete-access-key --user-name $user --access-key-id $key --profile $cred --region $region 

aws iam delete-user --user-name $user --profile $cred --region $region