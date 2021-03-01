"User model and helper functions"

# stdlib
from datetime import datetime
from typing import Tuple
# 3rd party
import bcrypt
from sqlalchemy import func
# local
from .. import db


class User(db.Model):

    "User model"

    __tablename__ = 'user'
    __table_args__ = (
        db.Index('idx_user_name_lower', func.lower('name')),
        db.Index('idx_user_email_lower', func.lower('email')),
    )

    #: Unique ID
    id = db.Column(db.Integer(), primary_key=True)
    #: User name
    name = db.Column(db.String(24), unique=True)
    #: Email address
    email = db.Column(db.String(64), unique=True)
    #: Encrypted password
    password = db.Column(db.LargeBinary(64))
    #: Password salt
    salt = db.Column(db.LargeBinary(32))
    #: Creation time
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    #: Last login
    last = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f'User({self.name}#{self.id})'

    @staticmethod
    def hash_password(pwd: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        Generate a hash for the given password and salt. If no salt is
        provided, one will be generated.

        :param pwd: The plain-text password to encrypt
        :param salt: The salt (if any) to use
        :returns: encrypted password, salt
        """

        if salt is None:
            salt = bcrypt.gensalt()

        password = bcrypt.hashpw(pwd.encode('utf8'), salt)

        return password, salt
