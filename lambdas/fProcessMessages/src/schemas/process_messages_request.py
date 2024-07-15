from typing import List, Dict

from aws_lambda_powertools.utilities.parser import BaseModel


class ProcessMessagesRequest(BaseModel):
    messages_info: List[Dict]

