"User model and helper functions"

# stdlib
from datetime import datetime
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

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(24), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary(64))
    salt = db.Column(db.LargeBinary(32))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    last = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f'User({self.name}#{self.id})'

    @staticmethod
    def hash_password(pwd, salt=None):
        'Generate a hash for the given password and salt; return (hash, salt)'

        if salt is None:
            salt = bcrypt.gensalt()

        password = bcrypt.hashpw(pwd.encode('utf8'), salt)

        return (password, salt)
