"""Demo schema"""

# 3rd party
from pydantic import BaseModel


class DemoResponse(BaseModel):

    """Demonstration response"""

    userland: bool
    """Dummy response value"""

    whoami: str
    """Current user's name"""
