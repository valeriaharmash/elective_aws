import boto3


class SnsService:
    def __init__(self):
        self.client = boto3.client('sns')

    def publish_sns_message(self, topic_arn: str, message_content: str, message_type: str):
        """
        Publish a message to an SNS topic with specific attributes.

        Parameters:
            topic_arn (str): The ARN of the SNS topic to publish the message to.
            message_content (str): The content of the message to be published.
            message_type (str): The type of the message, used as an attribute in the SNS message.

        Returns:
            None
        """
        self.client.publish(
            TopicArn=topic_arn,
            Message=message_content,
            MessageAttributes={
                "message_type": {
                    "DataType": "String",
                    "StringValue": message_type
                }
            }
        )
