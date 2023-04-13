##Description: Download the script from s3 then execute that to create a user as per the sso value that is entered in the parameer and place the corresponding ssh key. That is being used in the proxy command to get logged in the EC2-server witout using 'ssm' as well as bastion.

##Parameters:

BucketName: default: {{ssm:/automation/ami/bucket}} description: common bucket where script is stored. userName: default: Nothing description: "(Required) login user" like 'u' sshkey; default: Nothing description: "(Required) ssh public key"

##Applicable Accounts [Tagging]:

|Accounts   | Applicable  |
| ------------ | ------------ |
| 325381443140  | Yes |
| 762713699569  | Yes |
| 538462866776  | Yes |
| 100148143185  | Yes |
| 372444449616  | Yes |

