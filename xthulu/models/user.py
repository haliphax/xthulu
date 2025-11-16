"""User model and helper functions"""

# stdlib
from datetime import datetime
from typing import Any

# 3rd party
import bcrypt
from sqlmodel import Field, func, Index, SQLModel


class User(SQLModel, table=True):
    """User model"""

    id: int | None = Field(primary_key=True, default=None)
    """Unique ID"""

    name: str = Field(max_length=24, unique=True)
    """User name"""

    email: str = Field(max_length=64, unique=True)
    """Email address"""

    password: bytes | None = Field(max_length=64, default=None)
    """Encrypted password"""

    salt: bytes | None = Field(max_length=32, default=None)
    """Password salt"""

    created: datetime = Field(default_factory=datetime.now)
    """Creation time"""

    last: datetime = Field(default_factory=datetime.now)
    """Last login"""

    __table_args__ = (
        Index("idx_user_name_lower", func.lower("name")),
        Index("idx_user_email_lower", func.lower("email")),
    )

    def __init__(self, **data: Any):
        super(User, self).__init__(**data)

    def __repr__(self):  # pragma: no cover
        return f"User({self.name}#{self.id})"

    @staticmethod
    def hash_password(
        pwd: str, salt: bytes | None = None
    ) -> tuple[bytes, bytes]:
        """
        Generate a hash for the given password and salt. If no salt is
        provided, one will be generated.

        Args:
            pwd: The plain-text password to encrypt.
            salt: The salt to use, if any.

        Returns:
            The encrypted password and salt as a tuple.
        """

        if salt is None:
            salt = bcrypt.gensalt()

        password = bcrypt.hashpw(pwd.encode("utf-8"), salt)

        return password, salt
