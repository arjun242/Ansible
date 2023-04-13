import boto3
from os import path
import json
from botocore.exceptions import ClientError

"""
Class to publish the Audit SNS message

"""

class SNSSender:

    def __init__(self, session, topic_arn, subject, text_file, json_file):

        self.topic_arn = topic_arn
        self.subject = subject
        self.text_file = text_file
        self.json_file = json_file
        self.sns = session.client('sns')

    def publish(self):

        # get message structure
        message = self.get_message_structure()

        # publish the message
        try:
            response = self.sns.publish(
                TopicArn=self.topic_arn,
                Subject=self.subject,
                MessageStructure = 'json',
                Message=message    
            )
            print("Notification Published.  Message ID: {0}".format(response['MessageId']))

        # inform if error
        except ClientError as e:
            print("ERROR: Failed to publish SNS message")
            print(e)

    # Helper method
    
    def get_email_message(self):

        # read from message file and construct message

        if self.text_file and path.exists(self.text_file):
            with open(self.text_file, "r") as file:
                message_body = file.read()
                
        else:
            print('ERROR: Failed to locate file')
            exit(1)

        return message_body

    def get_json_message(self):
        
        # load json and return
        if self.json_file and path.exists(self.json_file):
            with open(self.json_file, "r") as file:
                json_message = json.load(file)
        
        return json.dumps(json_message, indent=2)

    def get_message_structure(self):

        # get messages
        email_message = self.get_email_message()

        #json_message for later use with lambda
        #json_message = self.get_json_message()

        # create jsons
        struct = {'default': email_message, 'email': email_message}
        json_data = json.dumps(struct)
        
        return json_data

        

            



        

        

