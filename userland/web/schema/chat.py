"""Chat schema"""

# stdlib
from typing import Any

# 3rd party
from pydantic import BaseModel


class ChatPost(BaseModel):
    """Posted chat message"""

    message: str
    """The message body"""

    token: str
    """The client's CSRF token"""

    def __init__(self, **data: Any):
        super().__init__(**data)


class ChatToken(BaseModel):
    """CSRF token"""

    token: str
    """The token value"""

    def __init__(self, **data: Any):
        super().__init__(**data)
