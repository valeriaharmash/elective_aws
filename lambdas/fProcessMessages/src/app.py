from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
from common_schemas.lambda_response import LambdaResponseBase
from aws_lambda_powertools import Logger
from schemas.process_messages_request import ProcessMessagesRequest
from run_process_messages import MessageProcessor

logger = Logger('process-messages-app')


@logger.inject_lambda_context
@event_parser
def lambda_handler(event: ProcessMessagesRequest, context: LambdaContext):
    try:
        message_processor = MessageProcessor()

        message_processor.process_messages(
           queue_url=event.QueueUrl,
           message_type=event.MessageType
        )
        message = 'Successfully processed messages.'
        logger.info(message)
    except Exception as e:
        logger.exception(f'Failed to process messages, reason: {e}')
        raise e
    return LambdaResponseBase(
        status_code=200,
        message=message
    ).model_dump()
