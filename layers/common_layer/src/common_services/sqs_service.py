from typing import List

import boto3


class SqsService:
    def __init__(self, region_name: str = 'us-east-1'):
        self.region_name = region_name
        self.client = boto3.client('sqs', region_name=self.region_name)

    def read_sqs_messages(self, queue_url: str, num_messages: int) -> List:
        """
            Reads messages from an SQS queue.

            Args:
                queue_url (str): The URL of the SQS queue from which to read messages.
                num_messages (int): The maximum number of messages to retrieve from the queue.

            Returns:
                List: A list of messages received from the queue. Each message is represented
                      as a dictionary containing message details.
        """
        response = self.client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=num_messages,
            WaitTimeSeconds=20
        )
        return response.get('Messages', [])
