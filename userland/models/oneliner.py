"""Oneliner model"""

# stdlib
from datetime import datetime

# 3rd party
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

# api
from xthulu import db
from xthulu.models import User


class Oneliner(db.Model):
    """Oneliner model"""

    __tablename__ = "oneliner"
    id = Column(Integer(), primary_key=True)
    user_id = Column(
        Integer(),
        ForeignKey(User.id, onupdate="cascade", ondelete="set null"),
        nullable=True,
    )
    message = Column(String(78))
    timestamp = Column(DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"Oneliner(#{self.id})"
