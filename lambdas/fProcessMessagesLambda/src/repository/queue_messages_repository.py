import json
from typing import List

from sqlalchemy.orm import scoped_session

from models.messages_processing.queue_messages import QueueMessage


class PostgresMessagesRepository:
    def __init__(self, db_session: scoped_session):
        self.db_session = db_session

    def ingest_message(self, messages: List):
        with self.db_session.begin() as session_transaction:
            with session_transaction.session as session:
                try:
                    queue_messages = []

                    for msg in messages:
                        body = msg['Body']
                        message_id = msg['MessageId']

                        queue_message = QueueMessage(
                            message_id=message_id,
                            message=body
                        )
                        queue_messages.append(queue_message)

                    session.add_all(queue_messages)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
