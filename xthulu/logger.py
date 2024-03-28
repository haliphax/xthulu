"""Logger setup"""

# stdlib
from logging import DEBUG, Formatter, getLogger, INFO, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from sys import stdout

# local
from .configuration import get_config

log = getLogger(__name__)
"""Root logger instance"""

formatter = Formatter(
    "{asctime} {levelname:<7} <{module}.{funcName}> {message}", style="{"
)
"""LogRecord formatter"""

fileHandler = TimedRotatingFileHandler("run/logs/xthulu.log", when="d")
"""Rotating file handler"""

streamHandler = StreamHandler(stdout)
"""Console stream handler"""

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)
log.addHandler(fileHandler)
log.addHandler(streamHandler)
log.setLevel(DEBUG if bool(get_config("debug.enabled", False)) else INFO)
