import boto3
from aws_lambda_powertools import Logger
from config import MSG_QUEUE_URL, MSG_DB_CREDENTIALS
from db_core import create_db_session
from repository.queue_messages_repository import PostgresMessagesRepository
logger = Logger('run-process-messages-view')


class MessageProcessor:
    def __init__(self):
        self.region_name = 'us-east-1'
        self.sqs_client = boto3.client('sqs', region_name=self.region_name)
        self.queue_url = MSG_QUEUE_URL
        self.repo = None
        self.db_session = None

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

    def read_messages(self):
        response = self.sqs_client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )

        messages = response.get('Messages', [])

        try:
            self.initialize_repo()

            self.repo.ingest_message(messages)
        except Exception as e:
            logger.info(f'Error ingesting message, reason: {e}')
            raise e

