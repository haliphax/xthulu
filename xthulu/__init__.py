"xthulu module initialization"

# stdlib
import logging
from os import environ
from os.path import dirname, join
import sys
# 3rd party
from gino import Gino
import toml

log = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(logging.Formatter(
    '{asctime} {levelname:<7} {module}.{funcName}: {message}', style='{'))
log.addHandler(streamHandler)
config = {}
config_file = (environ['XTHULU_CONFIG'] if 'XTHULU_CONFIG' in environ
               else join(dirname(__file__), '..', 'data', 'config.toml'))
config = toml.load(config_file)
log.setLevel(logging.DEBUG if config.get('debug', {}).get('enabled', False)
             else logging.INFO)

db = Gino()
