#!/usr/bin/env bash
# set up the system for the first time

set -eo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../data"

if [[ -f "config.toml" ]]; then
	echo "config.toml already exists; skipping"
else
	echo "creating config.toml from config.example.toml"
	cp config.example.toml config.toml
fi

if [[ -f "ssh_host_key" ]]; then
	echo "ssh_host_key already exists; skipping"
else
	echo "generating ssh_host_key"
	ssh-keygen -f ssh_host_key -t rsa -b 4096 -N ""
fi

cd ../docker
echo "building base image"
docker compose build base-image
echo "pulling service images"
docker compose pull --ignore-buildable
cd ../etc
echo "initializing database"
./cli.sh db create --seed
./userland.sh db create --seed
echo "building static web site"
./build-web.sh
