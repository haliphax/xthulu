"User model and helper functions"

# 3rd party
import bcrypt
# local
from .. import db


class User(db.Model):

    "User model"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(24), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary(64))
    salt = db.Column(db.LargeBinary(32))

    __tablename__ = 'user'
    __table_args__ = (
        db.Index('idx_user_name_lower', db.func.lower(name)),
        db.Index('idx_user_email_lower', db.func.lower(email)),
    )

    def __repr__(self):
        return f'User({self.name}#{self.id})'

    @staticmethod
    def hash_password(pwd, salt=None):
        'Generate a hash for the given password and salt; return (hash, salt)'

        if salt is None:
            salt = bcrypt.gensalt()

        password = bcrypt.hashpw(pwd.encode('utf8'), salt)

        return password, salt
