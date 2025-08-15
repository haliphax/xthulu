#!/usr/bin/env bash
# userland container shortcut

set -eo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../docker"
docker compose run --rm user $*
