import json
import os
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters
from common_schemas.credentials_schema import TopicArnCredential

logger = Logger('generate-send-messages-config')

if os.getenv('ENVIRONMENT') == 'local':

    topic_arn_secret = json.dumps({
        "arn": os.getenv('MSG_TOPIC_ARN')
    })
else:
    topic_arn_secret = parameters.get_secret(name=os.getenv('MSG_TOPIC_ARN_SECRET_NAME'))

try:
    MSG_TOPIC_ARN_CREDENTIALS = TopicArnCredential.model_validate_json(topic_arn_secret)
except Exception as e:
    err_msg = f'Failed to get secrets, reason: {e}'
    logger.error(err_msg)
    raise Exception(err_msg)
