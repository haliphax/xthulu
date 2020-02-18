"user model"

from .. import db


class User(db.Model):

    "User model"

    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True) 
    name = db.Column(db.Unicode(), unique=True)
