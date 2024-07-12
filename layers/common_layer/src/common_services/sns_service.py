import json

import boto3


class SnsService:
    def __init__(self):
        self.client = boto3.client('sns')

    def publish_sns_message(self, topic_arn: str, message_content: str, message_type: str):
        self.client.publish(
            TopicArn=topic_arn,
            Message=json.dumps({'default': message_content}),
            MessageStructure='String',
            MessageAttributes={
                "Name": {
                    "DataType": "String",
                    "StringValue": "message_type"
                },
                "Type": {
                    "DataType": "String",
                    "StringValue": "String"
                },
                "Value": {
                    "DataType": "String",
                    "StringValue": message_type
                }
            }
        )
