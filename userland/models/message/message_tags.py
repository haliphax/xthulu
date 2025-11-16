"""Message tag relationship model"""

# stdlib
from typing import Any

# 3rd party
from sqlmodel import Field, SQLModel

# api
from xthulu.resources import Resources

db = Resources().db


class MessageTags(SQLModel, table=True):
    """Message tag model"""

    message_id: int = Field(foreign_key="message.id", primary_key=True)
    """The tagged message ID"""

    tag_name: str = Field(foreign_key="message_tag.name", primary_key=True)
    """The name of the tag"""

    __tablename__ = "message_x_message_tag"  # type: ignore

    def __init__(self, **data: Any):
        super(MessageTags, self).__init__(**data)
