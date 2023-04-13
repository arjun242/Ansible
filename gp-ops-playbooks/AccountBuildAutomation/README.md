## Account Automation Check - Audit Process

### General Information

This folder contains code that automates the account validation process for GuardRails accounts.
This code maps to an account validation checklist which can be found [HERE](https://devcloud.swcoe.ge.com/devspace/display/WZSLF/Valid+Account+Checklist).
Account setup steps for a new GuardRails account can be found [HERE](https://devcloud.swcoe.ge.com/devspace/display/WZSLF/Account+Setup+Order).
There are several steps of the account validation process that have not been automated and must be done manually.  These are:

1. NACL must be approved by EA team
2. New account Splunk request must be setup
3. GitHub Org associated with account exists
4. "cft-infra-templates", "cft-infra-nacl", "cft-infra-app", and "cft-app-iam" repos within that GitHub org.
5. CI/CD pipeline setup for apps team to use and Jenkins instance in place
6. Verify that a join was performed for windows active directory

### Dependencies

* Must be able to generate an AWS account key: Gossamer3 https://gehosting.io/docs/identity/gossamer3#why-do-i-need-to-use-gossamer-3
* Must have Python3+ installed.
* Must have the Boto3 package installed.  To install from terminal run: <code>'pip install boto3'</code>
* Boto3 documentation can be found [HERE](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

### About the Code

The code was written to mirror the account validation checklist (linked above).  Several python classes correspond to sections in that document and each method generally maps to a task or tasks within that section.  There are some execptions however. These classes are: 

* ***IAMAuditer.py*** - queries details regarding Identity and Access Management Roles and Policies
* ***SSMAuditer.py*** - queries details regarding Systems Manager Documents and Associations
* ***StacksAuditer.py*** - queries details regarding Cloudformation Stacksets launched in account
* ***VPCAuider.py*** - queries details regarding VPC configurations such as Subnets, Gateways and Security Groups
* ***MISCAuditer.py*** - queries miscellaneous details such as KMS Key creation, EBS volume encryption, and SNS topics
* ***Helpers.py*** - contains several methods that are used by various other classes
* ***Summary.py*** - Reads ideal account config file and processes all reports in filesystem and builds a single excel summary doc.   

Other classes handle the exection of the auditers, writing their results to files, and publishing those results to SNS. They are:

* ***Main.py*** - Reads the list of accounts to audit, sequentially invokes audit (Runner.py) on each account, invokes Summary module to build excel audit summary to filesystem.
* ***Runner.py*** - ochestrates the entire audit, with the exception of one independent validation check. (see below)
* ***FileWriter.py*** - handles writing the results of the audit to two files, one in text format and the other in json format. These files are: <code>\<account-id\>.txt</code> and <code>\<account-id\>.json</code>
* ***SNSSender.py*** - class that publishes the audit report to the 'AccountAudit' topic in each GuardRails account.
* ***CheckBucketPolicy.py*** - queries gp-ops account to ensure that the id of the account under audit has permissions in several S3 buckets.

### Modifying the Code

Every auditer class has a <code>return_data()</code> method that runs each class method, captures their output, and nests it in dictionary with a class identifier e.g., <code>{'IAM': nested_dictionary}</code>.  The Runner class instantiates each class, calls its <code>return_data()</code> method, collects all these dictionaries and then passes them to the FileWriter object to write out in json and text.  You must follow this design pattern when adding to or modifying the code so the output format remains in tact.  The FileWriter.py file takes the json and parses it to write the text file.  You will also need to add logic here so that your modifications correctly make it into the text file.

All of the Gas Power Guardrails configrations exist within the config folder in a file named "ideal_account.yml". It contains a large YML object which contains all attributes we will be verifying during the audit process.

### About the Audit Role and Policy

A custom role was created to run this audit.  It's essentially the GP-Read-Only-Role with some small enhancements.  You can the find the details of the role [HERE](https://github.build.ge.com/gp-ops/global-stack-sets/tree/master/audit-fed).
Any new checks that you implement in this audit must be within the scope of the permissions set by the Audit role's policies, or you need to edit the AuditFedPolicy to include those permissions.  The process for this is to fork the repo in the link above, make your changes, open a PR, and contact an team member for review.

### Requesting Access to the Distribution List

In order to get access to the Audit role you must request to join the DL for the account you wish to audit.  These are the steps:

1. Go [HERE](https://oneidm.ge.com/)
2. Select 'Manage My Groups'
3. Select 'Join a Distribution List'
4. Leave 'All Businesses' in the first dropdown
5. In the second dropdown select 'By DL Name'
6. In the final dropdown put this string: AWS_hq/audit-fed
7. Click search and choose the DL for the account you wish to audit.

### Running the Audit

Run the following steps to invoke the audit.

1. Update the "account_list.yml" file (within the 'src' folder) to contain the accounts you would like to audit. Follow the format in the file. 
2. Generate credentials: https://gehosting.io/docs/identity/gossamer3#why-do-i-need-to-use-gossamer-3
    - You will need to generate your credentials in bulk by running the following command: 'gossamer3 -a default --skip-prompt bulk-login ..\config\account_list.yml --force' MAKE SURE YOU ARE IN THE 'SRC' FOLDER. You should see the credentials being written to your file system in the CMD terminal.
3. Run the following command: <code>py main.py</code>
    - This command will perform all audits, then write your account-audit-summary.xslx file. This will exist within the "src" folder. 

### Issues

* The account checklist asks to validate whether a patch baseline has been setup in SSM for prod and non-prod.  This baseline hasn't been implemented yet.  See Hamza for details.
* The subnets validation check assumes that each subnet has a tag of {'SubnetType': value}.  Aadesh manually applied these tags to some subnets in GR accounts but not others so this validation check will produce inconsistent/incorrect results until this tagging convention is solidified.
* There is no way to uniquley identify DLM snapshotting policies so that validation check has not been implemented.
* The output formatting of the text report is fine when written to file.  However, when it gets read in and sent as an SNS notification newline characters are ignored in some locations but not others, making the formatting awkward in certain places.   

### Potential Enhancements:
* Deep Comparison: The account audit tool currently checks for resources by confirming that the name string of the resource is present within the account. While this confirms that a control exists in the account with that name, it doesn't confirm that all cloud resources contain identical configurations. This would help us further drive concistency across our accounts.
* At the moment, existance of the ECR golden image (for each account) is not confirmed. We will need to create a new check for this field and include it within the audit tool.
* Convert to Lambda Function. As you can see, this script runs on the user's file system. We believe this would allow for better visibility and potential for implementing auto-remediation.

### Account Audit Spreadsheet:
When the script is finished running, it writes an excel file named 'account-audit-summary.xslx' to the 'src' folder. It contains the following worksheets: Bucket Policies, IAM-Roles, IAM-Policies, VPC-Security-Groups, VPC-Subnet-Types, VPC-Route-Tables, VPC-Misc, SSM-Documents, SSM-Windows, SSM-Parameters, SSM-Associations, StackSets, SubnetGroups, RDS-Parameter-Groups, RDS-Cluster-Parameter-Groups, Stacks-Misc, Config-Rules, Lambda-Functions, General-Misc.

Within each worksheet, we have the first three columns for Account Audit Information: Account Name, Account ID, Timestamp of audit. The remaining columns are for each of the expected controls. If the expected control has been found, it is marked with a "Done" and a green background. If the expected control is missing, it is marked with either a "Missing", "Failed" and is given a red background.

For an example account-audit-summary.xslx file, enter the 'src' folder and open up the file.

### New to AWS and Want to Add to add Validation Checks

If you are new to AWS and want to add to add a validation check but dont know where to start it will be useful to explore the AWS console Web GUI first.  This way you can visualize what you are looking to do before attempting to accomplish it through the Boto API or through the AWS CLI.  I've provided some screenshots below that depict manual validation checks as examples.

**Checking if Lambda function exists:**

![image](lambda.jpg)

**Checking if SNS Topic exists:**

![image](sns.jpg)

**Checking if Stack exists:**

![image](stack.jpg)

**Checking if IAM Role exists:**

![image](iam.jpg)

