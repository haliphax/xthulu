"""Context specific LogFilter implementation"""

# stdlib
from logging import Filter, LogRecord


class ContextLogFilter(Filter):
    """Custom logging.Filter that injects username and remote IP address"""

    username: str
    """The context user's username"""

    ip: str
    """The context user's IP address"""

    def __init__(self, username: str, ip: str):
        self.username = username
        self.ip = ip

    def filter(self, record: LogRecord):
        """
        Filter log record.

        @record: The record to filter.
        """

        record.username = self.username
        record.ip = self.ip

        return True
