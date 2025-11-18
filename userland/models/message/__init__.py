"""Message model"""

# stdlib
from datetime import datetime
from typing import Any, ClassVar, Optional

# 3rd party
from sqlmodel import Field, Relationship, SQLModel

# api
from xthulu.models.user import User


class Message(SQLModel, table=True):
    """Message model"""

    MAX_TITLE_LENGTH: ClassVar[int] = 120

    id: int | None = Field(primary_key=True, default=None)
    """Unique ID"""

    parent_id: int | None = Field(foreign_key="message.id", default=None)
    """Parent message ID (if any)"""

    parent: Optional["Message"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Message.id"},
    )
    """Parent message (if any)"""

    children: list["Message"] = Relationship(back_populates="parent")
    """Child messages"""

    author_id: int | None = Field(foreign_key="user.id", default=None)
    """Author ID of the message"""

    author: User | None = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Message.author_id == User.id",
        }
    )
    """Author of the message"""

    recipient_id: int | None = Field(foreign_key="user.id", default=None)
    """Recipient ID of the message (`None` for public messages)"""

    recipient: User | None = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Message.recipient_id == User.id",
        }
    )
    """Recipient of the message"""

    created: datetime = Field(default_factory=datetime.now)
    """Creation time"""

    title: str = Field(max_length=MAX_TITLE_LENGTH)
    """Title of the message"""

    content: str = Field()
    """The message's content"""

    def __init__(self, **data: Any):
        super(Message, self).__init__(**data)

    def __repr__(self):  # pragma: no cover
        return f"Message(#{self.id})"
