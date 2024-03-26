"""Message model"""

# stdlib
from datetime import datetime

# 3rd party
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

# api
from xthulu.resources import Resources
from xthulu.models import User

db = Resources().db


class Message(db.Model):
    """Message model"""

    id = Column(Integer(), primary_key=True)
    """Unique ID"""

    parent_id = Column(
        None,
        ForeignKey("message.id", onupdate="cascade", ondelete="set null"),
        nullable=True,
    )
    """Parent message (if any)"""

    parent: "Message | None"

    author_id = Column(
        None,
        ForeignKey(User.id, onupdate="cascade", ondelete="set null"),
        nullable=True,
    )
    """Author of the message"""

    author: User

    recipient_id = Column(
        None,
        ForeignKey(User.id, onupdate="cascade", ondelete="cascade"),
        nullable=True,
    )
    """Recipient of the message (`None` for public messages)"""

    recipient: User | None

    created = Column(DateTime(), default=datetime.utcnow, nullable=False)
    """Creation time"""

    title = Column(String(120), nullable=False)
    """Title of the message"""

    content = Column(Text(), nullable=False)
    """The message's content"""

    __tablename__ = "message"

    def __repr__(self):
        return f"Message(#{self.id})"
