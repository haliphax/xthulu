"""Demo schema"""

# 3rd party
from pydantic import BaseModel


class DemoResponse(BaseModel):
    whoami: str
    xthulu: bool
