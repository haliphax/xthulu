"User model and helper functions"

# type checking
from typing import Optional, Tuple

# stdlib
from datetime import datetime

# 3rd party
import bcrypt
from sqlalchemy import (
    Column,
    DateTime,
    func,
    Index,
    Integer,
    LargeBinary,
    String,
)

# local
from .. import db


class User(db.Model):
    "User model"

    __tablename__ = "user"
    __table_args__ = (
        Index("idx_user_name_lower", func.lower("name")),
        Index("idx_user_email_lower", func.lower("email")),
    )

    #: Unique ID
    id = Column(Integer(), primary_key=True)
    #: User name
    name = Column(String(24), unique=True)
    #: Email address
    email = Column(String(64), unique=True)
    #: Encrypted password
    password = Column(LargeBinary(64))
    #: Password salt
    salt = Column(LargeBinary(32))
    #: Creation time
    created = Column(DateTime(), default=datetime.utcnow)
    #: Last login
    last = Column(DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"User({self.name}#{self.id})"

    @staticmethod
    def hash_password(
        pwd: str, salt: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """
        Generate a hash for the given password and salt. If no salt is
        provided, one will be generated.

        :param pwd: The plain-text password to encrypt
        :param salt: The salt (if any) to use
        :returns: encrypted password, salt
        """

        if salt is None:
            salt = bcrypt.gensalt()

        password = bcrypt.hashpw(pwd.encode("utf8"), salt)

        return password, salt
