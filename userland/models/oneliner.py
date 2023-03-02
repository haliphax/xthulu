"""Oneliner model"""

# stdlib
from datetime import datetime

# 3rd party
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

# api
from xthulu.models import User
from xthulu.resources import Resources

db = Resources().db


class Oneliner(db.Model):

    """Oneliner model"""

    id = Column(Integer(), primary_key=True)
    """Unique ID"""

    user_id = Column(
        Integer(),
        ForeignKey(User.id, onupdate="cascade", ondelete="set null"),
        nullable=True,
    )
    """User who left the oneliner"""

    message = Column(String(78))
    """The oneliner message"""

    timestamp = Column(DateTime(), default=datetime.utcnow)
    """When the oneliner was posted"""

    __tablename__ = "oneliner"

    def __repr__(self):
        return f"Oneliner(#{self.id})"
