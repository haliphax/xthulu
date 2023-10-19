"""Chat schema"""

# 3rd party
from pydantic import BaseModel


class ChatPost(BaseModel):
    message: str
