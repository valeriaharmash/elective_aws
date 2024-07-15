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

        for message_type_dict in event.messages_info:
            for message_type in message_type_dict.keys():
                message_processor.process_messages(
                    message_type=message_type,
                    num_messages=message_type_dict[message_type]
                )

        message = 'Successfully processed messages.'
        logger.info(message)
        return LambdaResponseBase(
            status_code=200,
            message=message
        )
    except Exception as e:
        logger.exception(f'Failed to process messages, reason: {e}')
        raise e