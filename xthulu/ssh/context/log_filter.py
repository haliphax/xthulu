"""Context specific LogFilter implementation"""

# type checking
from typing import Literal

# stdlib
from logging import Filter, LogRecord


class ContextLogFilter(Filter):
    """Custom `logging.Filter` that injects username and remote IP address"""

    whoami: str
    """The context user's username@host information"""

    def __init__(self, whoami: str):
        """
        Create a new instance of this `logging.Filter`.

        Args:
            whoami: The connection information to inject.
        """
        self.whoami = whoami

    def filter(self, record: LogRecord) -> Literal[True]:
        """
        Filter log record.

        Args:
            record: The record to filter.

        Returns:
            Whether to persist the record.
        """

        record.whoami = self.whoami

        return True
