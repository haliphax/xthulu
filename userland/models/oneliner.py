"""Oneliner model"""

# stdlib
from datetime import datetime
from typing import ClassVar

# 3rd party
from sqlmodel import Field, Relationship, SQLModel

# api
from xthulu.models.user import User


class Oneliner(SQLModel, table=True):
    """Oneliner model"""

    MAX_LENGTH: ClassVar = 120
    """Maximum length of oneliner messages"""

    id: int | None = Field(primary_key=True, default=None)
    """Unique ID"""

    user_id: int | None = Field(foreign_key="user.id", default=None)
    """User ID of the author"""

    user: User | None = Relationship()
    """Author of the oneliner"""

    message: str = Field(max_length=MAX_LENGTH)
    """The oneliner message"""

    timestamp: datetime = Field(default_factory=datetime.now)
    """When the oneliner was posted"""

    def __repr__(self):
        return f"Oneliner(#{self.id})"
