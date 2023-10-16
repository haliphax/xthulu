"""Message tag model"""

# stdlib
from datetime import datetime

# 3rd party
from sqlalchemy import (
    Column,
    DateTime,
    String,
)

# local
from ...resources import Resources

db = Resources().db


class MessageTag(db.Model):

    """Message tag model"""

    name = Column(String(32), primary_key=True)
    """The tag's name"""

    created = Column(DateTime(), default=datetime.utcnow())
    """When the tag was created"""

    __tablename__ = "message_tag"

    def __repr__(self):
        return f"MessageTag({self.name})"
