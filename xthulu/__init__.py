"xthulu module initialization"

# stdlib
import logging
from os import environ
from os.path import dirname, join
import sys
# 3rd party
from yaml import safe_load

log = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(logging.Formatter(
    '{asctime} {levelname} {module}.{funcName}: {message}', style='{'))
log.addHandler(streamHandler)
config = {}
config_file = (environ['XTHULU_CONFIG'] if 'XTHULU_CONFIG' in environ
               else join(dirname(__file__), '..', 'data', 'config.yml'))

with open(config_file) as f:
    config = safe_load(f)

log.setLevel(logging.DEBUG
             if 'debug' in config
                and 'main' in config['debug']
                and config['debug']['main']
             else logging.INFO)
