"""User model and helper functions"""

# stdlib
from datetime import datetime

# 3rd party
import bcrypt
from sqlalchemy import (  # type: ignore
    Column,
    DateTime,
    func,
    Index,
    Integer,
    LargeBinary,
    String,
)

# local
from ..resources import Resources

db = Resources().db


class User(db.Model):  # type: ignore
    """User model"""

    id = Column(Integer(), primary_key=True)
    """Unique ID"""

    name = Column(String(24), unique=True, nullable=False)
    """User name"""

    email = Column(String(64), unique=True, nullable=False)
    """Email address"""

    password = Column(LargeBinary(64), nullable=True)
    """Encrypted password"""

    salt = Column(LargeBinary(32), nullable=True)
    """Password salt"""

    created = Column(DateTime(), default=datetime.utcnow, nullable=False)
    """Creation time"""

    last = Column(DateTime(), default=datetime.utcnow, nullable=False)
    """Last login"""

    __tablename__ = "user"
    __table_args__ = (
        Index("idx_user_name_lower", func.lower("name")),
        Index("idx_user_email_lower", func.lower("email")),
    )

    def __repr__(self):
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
