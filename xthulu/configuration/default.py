"""
Default configuration

This default configuration is used if no configuration file is found. If a
configuration file is loaded, this configuration is used as a base and the
loaded configuration is layered over the top of it.
"""

default_config = {
    "db": {
        "bind": "postgres://xthulu:xthulu@db:5432/xthulu",
    },
    "ssh": {
        "auth": {
            "bad_usernames": [
                "admin",
                "administrator",
                "root",
                "system",
                "god",
            ],
            "no_password": ["guest"],
        },
        "host": "0.0.0.0",
        "host_keys": ["data/ssh_host_key"],
        "port": 8022,
        "proxy_protocol": True,
        "userland": {
            "paths": ["userland/scripts"],
            "top": ["top"],
        },
    },
}
"""Default configuration"""