"""Message tag relationship model"""

# 3rd party
from sqlalchemy import (
    Column,
    ForeignKey,
)

# api
from xthulu.resources import Resources

db = Resources().db


class MessageTags(db.Model):
    """Message tag model"""

    message_id = Column(
        None,
        ForeignKey("message.id", onupdate="cascade", ondelete="cascade"),
        nullable=False,
    )
    """The tagged message ID"""

    tag_name = Column(
        None,
        ForeignKey("message_tag.name", onupdate="cascade", ondelete="cascade"),
        nullable=False,
    )
    """The name of the tag"""

    __tablename__ = "message_x_message_tag"
