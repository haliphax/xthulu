"""Logger setup"""

# stdlib
import gzip
from logging import Formatter, getLogger, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from os import path, remove
from shutil import copyfileobj
from sys import stdout

# local
from .configuration import get_config


def namer(name: str):
    """Name rotated files with *.gz extension."""

    return name + ".gz"


def rotator(source: str, dest: str):
    """Gzip files during rotation."""

    with open(source, "rb") as f_in:
        with gzip.open(dest, "wb") as f_out:
            copyfileobj(f_in, f_out)  # type: ignore

    remove(source)


log = getLogger(__name__)
"""Root logger instance"""

formatter = Formatter(
    "{asctime} {levelname:<7} <{module}.{funcName}> {message}", style="{"
)
"""LogRecord formatter"""

fileHandler = TimedRotatingFileHandler(
    path.join("run", "logs", "xthulu.log"), when="d"
)
"""Rotating file handler"""

fileHandler.rotator = rotator
fileHandler.namer = namer

streamHandler = StreamHandler(stdout)
"""Console stream handler"""

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)
log.addHandler(fileHandler)
log.addHandler(streamHandler)
log.setLevel(str(get_config("logging.level", "INFO")).upper())
