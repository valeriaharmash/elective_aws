from aws_lambda_powertools import Logger
from config import MSG_DB_CREDENTIALS
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
            "notification": NotificationMessage,
            "critical_alert": CriticalAlert
        }

    def initialize_repo(self) -> None:
        """
             Initialize the repository for processing messages. Creates a database session and
             assigns a PostgresMessagesRepository instance to the 'repo' attribute.

             If the repository is already initialized, it will do nothing.
         """
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

    def process_messages(self,  queue_url: str, message_type: str) -> None:
        """
        Process messages from an SQS queue by retrieving, ingesting, and deleting them.

        Parameters:
            queue_url (str): The URL of the SQS queue to retrieve messages from.
            message_type (str): The type of messages to process, used to select the appropriate model.
        """
        try:
            logger.info(f'Retrieving messages from "{queue_url}"...')

            messages = self.sqs_service.read_sqs_messages(queue_url=queue_url)

            logger.info(f'Successfully retrieved {len(messages)} messages from queue.')
        except Exception as e:
            logger.info(f'Error retrieving messages from  queue, reason: {e}')
            raise e

        try:
            self.initialize_repo()

            logger.info(f'Ingesting {len(messages)} into db...')

            model = self.models_dict[message_type]

            self.repo.ingest_messages(messages=messages, model=model)

            logger.info(f'Successfully ingested messages into "{model}".')
        except Exception as e:
            logger.info(f'Error ingesting message, reason: {e}')
            raise e

        try:
            self.sqs_service.delete_sqs_messages(messages=messages, queue_url=queue_url)
            logger.info(f'Successfully deleted {len(messages)} from {queue_url}.')
        except Exception as e:
            logger.info(f'Error deleting messages from "{queue_url}", reason: {e}')
            raise e

