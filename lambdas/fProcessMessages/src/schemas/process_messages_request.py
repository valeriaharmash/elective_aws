from typing import List, Dict

from aws_lambda_powertools.utilities.parser import BaseModel


class ProcessMessagesRequest(BaseModel):
    QueueUrl: str
    MessageType: str
    MessageBody: Dict
