#!/bin/ash

set -eo pipefail

if [[ "$1" != "start" ]]; then
	su -l xthulu -c "/usr/local/bin/python3 /app/entrypoint.py $*"
	exit $!
fi

ip rule add from 127.0.0.1/8 iif lo table 123
ip route add local 0.0.0.0/0 dev lo table 123

/go-mmproxy -l "0.0.0.0:22" -4 "127.0.0.1:8022" &
su -l xthulu -c "/usr/local/bin/python3 /app/entrypoint.py start"
