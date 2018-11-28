"xthulu python 3 asyncio BBS software"

# stdlib
from os import environ
from os.path import dirname, join
# 3rd party
from yaml import safe_load

config = {}


def load_config():
    "Load configuration"

    global config

    config_file = (environ['XTHULU_CONFIG'] if 'XTHULU_CONFIG' in environ
                   else join(dirname(__file__), '..', 'data', 'config.yml'))

    with open(config_file) as f:
        config = safe_load(f)

load_config()
