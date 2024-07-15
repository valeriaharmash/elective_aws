import boto3
from aws_lambda_powertools import Logger
from config import MSG_DB_CREDENTIALS, NOTIFICATIONS_QUEUE_URL, CRITICAL_ALERTS_QUEUE_URL
from db_core import create_db_session
from repository.queue_messages_repository import PostgresMessagesRepository
from common_services.sqs_service import SqsService
from models.messages_processing.notification_messages import NotificationMessage
from models.messages_processing.critical_alerts import CriticalAlert

logger = Logger('run-process-messages-view')


class MessageProcessor:
    def __init__(self):
        self.sqs_service = SqsService()
        self.repo = None
        self.db_session = None
        self.models_dict = {
            "notifications": NotificationMessage,
            "critical_alerts": CriticalAlert
        }
        self.queue_urls_dict = {
            "notifications": NOTIFICATIONS_QUEUE_URL,
            "critical_alerts": CRITICAL_ALERTS_QUEUE_URL
        }

    def initialize_repo(self) -> None:
        if self.repo is None:
            try:
                logger.info('Creating db session...')
                self.db_session = create_db_session(
                   db_url=MSG_DB_CREDENTIALS.get_db_url('postgresql', 'psycopg2')
                )
                self.repo = PostgresMessagesRepository(db_session=self.db_session)
                logger.info('Successfully created db session.')
            except Exception as e:
                logger.exception(f'Failed to create db session, reason: {e}')
                raise e

    def process_messages(self, message_type: str, num_messages: int) -> None:
        try:
            logger.info(f'Retrieving messages of type "{message_type}" from queue...')

            queue_url = self.queue_urls_dict[message_type]

            messages = self.sqs_service.read_sqs_messages(queue_url=queue_url, num_messages=num_messages)

            logger.info(f'Successfully retrieved {len(messages)} messages from queue.')
        except Exception as e:
            logger.info(f'Error retrieving messages from "{message_type}" queue, reason: {e}')
            raise e

        try:
            self.initialize_repo()

            logger.info(f'Ingesting {num_messages} into db...')

            model = self.models_dict[message_type]

            self.repo.ingest_messages(messages=messages, model=model)

            logger.info(f'Successfully ingested messages into {model}.')
        except Exception as e:
            logger.info(f'Error ingesting message, reason: {e}')
            raise e

