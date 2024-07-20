import json
from typing import List, Type

from sqlalchemy.orm import scoped_session
from db_core import Base


class PostgresMessagesRepository:
    def __init__(self, db_session: scoped_session):
        self.db_session = db_session

    def ingest_messages(self, messages: List, model: Type[Base]) -> None:
        """
            Ingests messages from an SQS queue into the database.

            Args:
                messages (List): List of SQS messages containing 'Body' and 'MessageId' fields.
                model (Base): SQLAlchemy model class representing the table structure to store messages.

            Returns: None
        """
        with self.db_session.begin() as session_transaction:
            with session_transaction.session as session:
                try:
                    queue_messages = []
                    for msg in messages:

                        message_id = msg['MessageId']
                        message_text = json.loads(msg['Body'])['Message']

                        queue_message = model(
                            message_id=message_id,
                            message=message_text
                        )
                        queue_messages.append(queue_message)

                    session.add_all(queue_messages)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
