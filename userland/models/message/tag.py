"""Message tag model"""

# stdlib
from datetime import datetime

# 3rd party
from sqlmodel import Field, SQLModel


class MessageTag(SQLModel, table=True):
    """Message tag model"""

    name: str | None = Field(max_length=32, primary_key=True, default=None)
    """The tag's name"""

    created: datetime = Field(default_factory=datetime.now)
    """When the tag was created"""

    __tablename__ = "message_tag"  # type: ignore

    def __repr__(self):  # pragma: no cover
        return f"MessageTag({self.name})"
