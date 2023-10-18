"""Chat schema"""

from pydantic import BaseModel


class ChatPost(BaseModel):
    message: str
