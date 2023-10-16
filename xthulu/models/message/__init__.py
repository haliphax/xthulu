"""Message model"""

# stdlib
from datetime import datetime

# 3rd party
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)

# local
from ...resources import Resources
from ..user import User

db = Resources().db


class Message(db.Model):

    """Message model"""

    id = Column(Integer(), primary_key=True)
    """Unique ID"""

    author_id = Column(
        None,
        ForeignKey(User.id, onupdate="cascade", ondelete="set null"),
        nullable=True,
    )
    """Author of the message"""

    recipient_id = Column(
        None,
        ForeignKey(User.id, onupdate="cascade", ondelete="cascade"),
        nullable=True,
    )
    """Recipient of the message (`None` for public messages)"""

    created = Column(DateTime(), default=datetime.utcnow)
    """Creation time"""

    content = Column(Text())
    """The message's content"""

    __tablename__ = "message"

    def __repr__(self):
        return f"Message(#{self.id})"
