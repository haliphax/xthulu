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
eval "\$(pyenv init -)"
eval "\$(pyenv virtualenv-init -)"
EOF
/home/$USER/.pyenv/bin/pyenv install 3.11

# install application and prerequisites, virtual env config, dev tools
/home/$USER/.pyenv/bin/pyenv virtualenv 3.11 xthulu
echo "pyenv activate xthulu" >> /home/$USER/.bashrc
cp .devcontainer/docker-compose.override.yml .
sudo su $USER -s /bin/bash /bin/bash -c "
	export PATH=\"\$HOME/.pyenv/versions/3.11/envs/xthulu/bin:\$PATH\";
	cd /workspaces/xthulu
	pip install -Ue .[dev]
	pre-commit install --install-hooks
	docker-compose build
	docker-compose pull
	"
