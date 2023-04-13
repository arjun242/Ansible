import boto3
import json
import string
import ast
from collections import defaultdict

# creating boto3 client
client=boto3.client('ssm',
aws_access_key_id  = "{{ aws_access_key_id }}",
aws_secret_access_key = "{{ aws_secret_access_key }}",
aws_session_token = "{{ aws_session_token }}",
region_name= "{{ region_name }}")

#Get parameter
def getparameter():
     return client.get_parameter(
          Name= '/automation/region-account',
          WithDecryption=True
          )


#Put the parameter
def putparamter(parameter_value):
     return client.put_parameter(
          Name= '/automation/region-account', 
          Value=parameter_value,
          Overwrite=True                                           #to allow to overwrite in the parameter store.
)

# executing the doc
def execute_doc():
     return client.start_automation_execution(
          DocumentName='share_existing_ssm_doc'
    
)
if __name__=="__main__":
     #calling getparameter
     ssm=getparameter()
     print(ssm.get("Parameter").get("Value"))
     print(json.dumps(ssm,indent=4,default=str))
     
     #updating the value feild
     ssm_value = ssm.get("Parameter").get("Value")                       #Calling parametere & value
     ssm_value = json.loads(ssm_value.replace("\'", "\""))              #replacing ' with " "
     region_name = "{{ region_name }}"
     region_dict = []                                                    #empty list
     if region_name in ssm_value.keys():
          region_dict = ssm_value[region_name]                           #calling region
     
     acc="{{ account_id }}"
     if len(acc)==12 and acc.isdigit:                                     # account id should be of 12 digit and only numbers
          region_dict.append(acc)                                         #appending
     ssm_value[region_name] = region_dict 
     ssm['Parameter']['Value'] = ssm_value

     print(json.dumps(ssm,indent=4,default=str))
     print(ssm_value)

    # print(str(putparamter(ssm)))
     

