#!/bin/bash

# fail on any errors
set -eo pipefail

# prerequisites for setting up python 3.11
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
	build-essential curl libbz2-dev libffi-dev libncurses-dev libreadline-dev \
	libsqlite3-dev libssl-dev lsb-release lzma-dev zlib1g-dev

# install and configure pyenv
curl -L \
	https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

cat >> /home/$USER/.bashrc <<EOF
PYENV_ROOT="\$HOME/.pyenv"
command -v pyenv >/dev/null || PATH="\$PYENV_ROOT/bin:\$PATH"
PATH="\$PYENV_ROOT/versions/xthulu/bin:\$PATH"
eval "\$(pyenv init -)"
eval "\$(pyenv virtualenv-init -)"
EOF

PYENV_ROOT="$HOME/.pyenv"
PATH="$PYENV_ROOT/versions/xthulu/bin:$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.11

# install application and prerequisites, virtual env config, dev tools
pyenv virtualenv 3.11 xthulu
echo xthulu > .python-version
cp .devcontainer/docker-compose.override.yml .
pip install -Ue .[dev,hiredis]
nodeenv -p
npm ci
pre-commit install --install-hooks
etc/gitmoji-hook.sh
cd docker || exit 1
docker compose build
