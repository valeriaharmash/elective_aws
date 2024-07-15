import json
import os
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities import parameters
from common_schemas.credentials_schema import DbCredential

logger = Logger('generate-process-messages-config')

CRITICAL_ALERTS_QUEUE_URL = os.getenv('CRITICAL_ALERTS_QUEUE_URL')
NOTIFICATIONS_QUEUE_URL = os.getenv('NOTIFICATIONS_QUEUE_URL')

if os.getenv('ENVIRONMENT') == 'local':

    db_secret = json.dumps({
        "host": os.getenv('MSG_DB_HOST'),
        "port": os.getenv('MSG_DB_PORT'),
        "password": os.getenv('MSG_DB_PASSWORD'),
        "username": os.getenv('MSG_DB_USERNAME'),
        "database": os.getenv('MSG_DB_DATABASE')
    })
else:
    db_secret = parameters.get_secret(name=os.getenv('MSG_DB_SECRET_NAME'))

try:
    MSG_DB_CREDENTIALS = DbCredential.model_validate_json(db_secret)
except Exception as e:
    err_msg = f'Failed to get secrets, reason: {e}'
    logger.error(err_msg)
    raise Exception(err_msg)

