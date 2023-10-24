#!/usr/bin/env bash
# build static web assets

set -eo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
node_ver="$(cat ../.nvmrc | sed -e 's/\n//' | sed -e 's/\//-/')"
docker run -it --rm -u "$UID:$GID" -v "$(pwd)/..:/app" -w /app \
	"node:$node_ver" npm run build
