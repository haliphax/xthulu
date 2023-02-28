"""xthulu module initialization"""

# type checking
from typing import Any

# stdlib
from logging import DEBUG, INFO
from os import environ
from os.path import exists, join

# 3rd party
from gino import Gino
from toml import load

# local
from .encodings import register_encodings
from .logger import log

config: dict[str, Any] = {}
"""xthulu configuration"""

config_file = (
    environ["XTHULU_CONFIG"]
    if "XTHULU_CONFIG" in environ
    else join("data", "config.toml")
)
"""xthulu configuration file"""

if exists(config_file):
    config = load(config_file)
else:
    log.warn(f"Configuration file not found: {config_file}")

log.setLevel(DEBUG if config.get("debug", {}).get("enabled", False) else INFO)

db = Gino()
"""Gino database API instance"""

register_encodings()
