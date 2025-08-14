# Contributor guide

⚠️ Contribution at this point is not recommended, but isn't necessarily
unwelcome. Please [open an issue][] with the `enhancement` label with your
proposed changes before beginning any work in earnest.

## Virtual environment

It is all but _required_ that you use a Python virtual environment for
development. These instructions will assume that you are using [pyenv][], and
have already installed and configured it on your system.

If you are using [Dev Containers][], you may use the repository's configuration
to create a new development container. Its `onCreateCommand` script will handle
all of the steps detailed below.

### Create the environment

```shell
pyenv install 3.12  # if 3.12 isn't already installed
pyenv virtualenv 3.12 xthulu
pyenv activate xthulu
```

### Install dependencies

In addition to the standard dependencies for the project, a set of
developer-focused dependencies are included. Some of them are located in the
`dev` optional dependencies bundle from the project's Python package, but others
come from the [node.js][] ecosystem. You should use a node version manager such
as [nvm][] in order to select the appropriate runtime version.

```shell
pip install -e .[dev,hiredis]
nvm install
nvm use
npm ci
```

## Configure development tools

### pre-commit

This project makes use of the [pre-commit][] system. The following applications
are used to lint source code and check formatting:

- [ESLint][] - TypeScript linter/formatter
- [Prettier][] - Miscellaneous formatter
- [Ruff][] - Python linter/formatter

You must initialize the system and install the appropriate hooks. Once
installed, they will be invoked automatically when you commit.

```shell
pre-commit install --install-hooks
```

### gitmoji

For conventional commit messages, this project has adopted the [gitmoji][]
standard. The `prepare-commit-msg` hook for crafting appropriately-categorized
commit messages can be installed with the provided script.

```shell
etc/gitmoji-hook.sh
```

### docker compose

In order to avoid the need to rebuild the service containers' base image each
time you make changes to the source code, you can create an override
configuration for the `docker compose` stack. This configuration will mount the
live source code directory into the running containers so that restarting them
should be sufficient to pick up any changes.

ℹ️ Userland scripts do not require a restart; a new session will import a fresh
copy of the file(s). Changes to static web resources (HTML, CSS, Javascript,
images) should be reflected immediately upon reloading the browser.

<details>
<summary>docker/docker-compose.override.yml</summary>

```yaml
version: "3"

x-live-source: &live-source
  volumes:
    - ../xthulu:/app/xthulu:ro

services:
  cli: *live-source
  user: *live-source
  ssh: *live-source
  web: *live-source

  web-static:
    volumes:
      # parent volume cannot be read-only or subvolumes will not mount
      - ../xthulu/web/static:/usr/share/nginx/html
      - ../userland/web/static:/usr/share/nginx/html/user:ro
```

</details>

## Unit tests

### Framework

The project's chosen testing framework is `pytest`.

```shell
# run tests, type checks, and generate coverage report
pytest --mypy --cov xthulu --ignore userland
```

### Test coverage

The [coverage][] application is used to calculate test coverage after unit tests
have been run. You may view the cached report at any time:

```shell
coverage report
```

[coverage]: https://coverage.readthedocs.io/en/latest/
[dev containers]: https://containers.dev/
[eslint]: https://eslint.org/
[gitmoji]: https://gitmoji.dev
[node.js]: https://nodejs.org
[nvm]: https://github.com/nvm-sh/nvm
[open an issue]: https://github.com/haliphax/xthulu/issues/new?labels=enhancement&title=Proposal:%20
[pre-commit]: https://pre-commit.com/
[prettier]: https://prettier.io/
[pyenv]: https://github.com/pyenv/pyenv
[ruff]: https://beta.ruff.rs/docs/
