"""Demo schema"""

# 3rd party
from pydantic import BaseModel


class DemoResponse(BaseModel):

    """Demonstration response"""

    whoami: str
    """Current user's name"""

    xthulu: bool
    """Dummy response value"""
