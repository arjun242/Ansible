import json
import yaml
import sys
import os
import boto3
from CheckBucketPolicy import CheckBucketPolicy 
from Runner import Runner
from Summary import Summary 

# fetch list of accounts to audit
def fetch_account_list_file():
    with open('/tmp/account-automation-folder/account-audit-service/config/account.yml', 'r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)

# declare main function which will invoke process
def main():

    # render accounts to be audited
    accounts = fetch_account_list_file()

    # iterate through all accounts, set environment variables, run kevin's script, all dynamically
    for account in accounts['roles']:

        print("{} NOW PROCESSING ACCOUNT: {} {}".format("\n",account['name'], "\n"))
        
        # update AWS profile to be gp-ops audit fed
        gp_ops_audit_role_arn = 'arn:aws:iam::325381443140:role/hq/audit-fed' 

        # extract account ID from the target account we're iterating through
        targetAccountId = account['profile'].split("_")[0]

        # check gp-ops bucket policy script, generate bucket-policy-file
        CheckBucketPolicy( targetAccountId, gp_ops_audit_role_arn, account['region'])

        # invoke auditor utility, generate the reports for this account data pair
        Runner(account['region'], account['name'], account['primary_role_arn'], account['customConfig'])
		  
	# build final speadsheet with summary from all audit report JSON files
    Summary()

main()
