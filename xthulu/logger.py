"""Logger setup"""

# stdlib
from sys import stdout
import logging

log = logging.getLogger(__name__)
"""Root logger instance"""

streamHandler = logging.StreamHandler(stdout)
streamHandler.setFormatter(
    logging.Formatter(
        "{asctime} {levelname:<7} <{module}.{funcName}> {message}", style="{"
    )
)
log.addHandler(streamHandler)
