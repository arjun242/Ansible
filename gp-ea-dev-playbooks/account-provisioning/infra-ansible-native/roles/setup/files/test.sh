#!/bin/bash

stackExist=$(aws cloudformation describe-stacks --stack-name iam-policy-bu-pw-ReadOnly --query 'Stacks[*].[StackStatus]')
result=$?
echo $result 
#Stack does not exist create
if [ $result -ne 0 ]; then
  echo "create stack for execution role"  
else
  echo "update existing stack"
fi