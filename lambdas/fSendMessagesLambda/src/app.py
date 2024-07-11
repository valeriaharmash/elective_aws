from aws_lambda_powertools.utilities.typing import LambdaContext
from common_schemas.lambda_response import LambdaResponseBase
from aws_lambda_powertools import Logger
import boto3
from config import MSG_QUEUE_URL, AWS_REGION

logger = Logger('send-messages-app')


@logger.inject_lambda_context
def lambda_handler(event, context: LambdaContext):
    region_name = AWS_REGION

    sqs = boto3.client('sqs', region_name=region_name)

    queue_url = MSG_QUEUE_URL

    num_messages = 100
    try:
        for i in range(1, num_messages + 1):
            message_body = f'Message {i} from Lambda!'

            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body
            )

        message = f"Message"
        logger.info(f'{message}')
        return LambdaResponseBase(
            status_code=200,
            message=message
        )
    except Exception as e:
        logger.exception(f'Failed, reason: {e}')
        raise e
