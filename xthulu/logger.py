"""Logger setup"""

# stdlib
from logging import DEBUG, Formatter, getLogger, INFO, StreamHandler
from sys import stdout

# local
from .configuration import get_config

log = getLogger(__name__)
"""Root logger instance"""

streamHandler = StreamHandler(stdout)
streamHandler.setFormatter(
    Formatter(
        "{asctime} {levelname:<7} <{module}.{funcName}> {message}", style="{"
    )
)
log.addHandler(streamHandler)
log.setLevel(DEBUG if bool(get_config("debug.enabled", False)) else INFO)
