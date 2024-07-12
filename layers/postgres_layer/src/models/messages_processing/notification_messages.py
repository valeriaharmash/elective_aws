from sqlalchemy import Column, Integer, VARCHAR, Text, DateTime
from sqlalchemy.sql import func

from db_core import Base


class NotificationMessage(Base):
    __tablename__ = 'notification_messages'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    message_id = Column(VARCHAR(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
