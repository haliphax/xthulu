"Oneliner model"

# stdlib
from datetime import datetime
# api
from xthulu import db
from xthulu.models import User


class Oneliner(db.Model):

    "Oneliner model"

    __tablename__ = 'oneliner'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id,
                                                    onupdate='cascade',
                                                    ondelete='set null'),
                        nullable=True)
    message = db.Column(db.String(78))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f'Oneliner(#{self.id})'
