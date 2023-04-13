## Description: Executes the document to check crowdstrike is running or not at all EC2 instances, if not install and configure it there.

## Scope: This document is setup to work with Window, Centos 7, Amazon Linux and Amazon Linux 2

## Parameters:

BucketName: default: {{ssm:/automation/ami/bucket}} description: common bucket from where binary will get installed. This will be comming from teh centralized gp-ops account.


## Setup:

Each downstream account will need permissions to download the proper binary.  The current target bucket is gp-us-east-ops-automation-common-tools.  Full path is gp-us-east-ops-automation-common-tools/cloud-strike

To enable cross account access modify the bucket policy for the following sid:
```
{
    "Sid": "Enable anonymous GET from every VPC",
    "Effect": "Allow",
    "Principal": {
        "AWS": [
            "arn:aws:iam::538462866776:root",
            "arn:aws:iam::564772463473:root",
            "arn:aws:iam::762713699569:root",
            "arn:aws:iam::372444449616:root",
            "arn:aws:iam::243553853704:root"
        ]
    },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::gp-us-east-ops-automation-common-tools/*"
}
```

Depending on the role you are executing the document with, you may have to add additional permissions to that role to be able to getObject from the target bucket.

##Applicable Accounts [Tagging]:

|Accounts   | Applicable  |
| ------------ | ------------ |
| 325381443140  | Yes |
| 762713699569  | Yes |
| 538462866776  | Yes |
| 100148143185  | Yes |
| 372444449616  | Yes |

