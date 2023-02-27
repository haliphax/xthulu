"""xthulu module initialization"""

# stdlib
import logging
from os import environ
from os.path import exists, join
import sys

# 3rd party
from gino import Gino
import toml

# local
from .encodings import register_encodings

log = logging.getLogger(__name__)
"""Root logger instance"""

streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(
    logging.Formatter(
        "{asctime} {levelname:<7} {module}.{funcName}: {message}", style="{"
    )
)
log.addHandler(streamHandler)

config = {}
"""xthulu configuration"""

config_file = (
    environ["XTHULU_CONFIG"]
    if "XTHULU_CONFIG" in environ
    else join("data", "config.toml")
)

if exists(config_file):
    config = toml.load(config_file)
else:
    log.warn(f"Configuration file not found: {config_file}")

log.setLevel(
    logging.DEBUG
    if config.get("debug", {}).get("enabled", False)
    else logging.INFO
)

db = Gino()
"""Gino database API instance"""

register_encodings()
