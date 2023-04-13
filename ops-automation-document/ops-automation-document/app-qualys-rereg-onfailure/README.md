##Description: Executes the document to check qualys is running or not at all EC2 instances, if not install and configure it there.

##Parameters:

BucketName: default: {{ssm:/automation/ami/bucket}} description: common bucket from where binary will get installed.
QualysActivationId: default: {{ssm:/automation/qualys/activationid}} description: qualys activation id.
QualysCustomerId: default: {{ssm:/automation/qualys/customerid}}  description: qualys coustomer id


##Applicable Accounts [Tagging]:

|Accounts   | Applicable  |
| ------------ | ------------ |
| 325381443140  | Yes |
| 762713699569  | Yes |
| 538462866776  | Yes |
| 100148143185  | Yes |
| 372444449616  | Yes |

