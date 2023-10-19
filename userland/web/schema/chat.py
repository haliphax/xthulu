"""Chat schema"""

# 3rd party
from pydantic import BaseModel


class ChatPost(BaseModel):

    """Posted chat message"""

    message: str
    """The message body"""
