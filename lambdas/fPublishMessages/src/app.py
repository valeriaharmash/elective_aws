from aws_lambda_powertools.utilities.typing import LambdaContext
from common_schemas.lambda_response import LambdaResponseBase
from aws_lambda_powertools import Logger
from common_services.sns_service import SnsService
from config import MSG_TOPIC_ARN_CREDENTIALS

logger = Logger('publish-messages-app')


@logger.inject_lambda_context
def lambda_handler(event, context: LambdaContext):
    try:
        sns_service = SnsService()
        topic_arn = MSG_TOPIC_ARN_CREDENTIALS.arn
        num_messages = 2

        for i in range(1, num_messages + 1):
            logger.info(f'Publishing general notification message {i}')
            sns_service.publish_sns_message(
                topic_arn=topic_arn,
                message_content=f'This is a general notification {i}.',
                message_type='notification'
            )

            logger.info(f'Publishing critical alert message {i}')
            sns_service.publish_sns_message(
                topic_arn=topic_arn,
                message_content=f'This is a critical alert {i}.',
                message_type='critical_alert'
            )
        message = 'Messages published successfully.'
        logger.info(message)
    except Exception as e:
        logger.exception(f'Failed to publish messages, reason: {e}')
        raise e
    return LambdaResponseBase(
        status_code=200,
        message=message
    ).model_dump()
