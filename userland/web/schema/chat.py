"""Chat schema"""

# 3rd party
from pydantic import BaseModel


class ChatPost(BaseModel):
    """Posted chat message"""

    message: str
    """The message body"""

    token: str
    """The client's CSRF token"""


class ChatToken(BaseModel):
    """CSRF token"""

    token: str
    """The token value"""
