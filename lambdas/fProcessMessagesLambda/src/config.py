import json
import os

from aws_lambda_powertools.utilities import parameters
from common_schemas.credentials_schema import DbCredential
MSG_QUEUE_URL = os.getenv('MSG_QUEUE_URL')

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
    raise Exception(err_msg)

