"User model and helper functions"

# 3rd party
import bcrypt
from sqlalchemy import func
# local
from .. import db


class User(db.Model):

    "User model"

    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=24), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary(64))
    salt = db.Column(db.LargeBinary(32))

    def __repr__(self):
        'Represent as str'

        return 'User({}#{})'.format(self.name, self.id)


idx_name_lower = db.Index('idx_user_name_lower', func.lower(User.name))
idx_email_lower = db.Index('idx_user_email_lower', func.lower(User.email))


def hash_password(pwd, salt=None):
    'Generate a hash for the given password and salt; return (hash, salt)'

    if salt is None:
        salt = bcrypt.gensalt()

    password = bcrypt.hashpw(pwd.encode('utf8'), salt)

    return (password, salt)
