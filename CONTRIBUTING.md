# Contributor guide

⚠️ Contribution at this point is not recommended, but isn't necessarily
unwelcome.

## Virtual environment

It is all but _required_ that you use a Python virtual environment for
development. These instructions will assume that you are using [pyenv], and have
already installed and configured it on your system.

If you are using [Dev Containers], you may use the repository's configuration to
create a new development container. Its `onCreateCommand` script will handle all
of the steps detailed below.

### Create the environment

```shell
pyenv install 3.11  # if 3.11 isn't already installed
pyenv virtualenv 3.11 xthulu
pyenv activate xthulu
```

### Install dependencies

In addition to the standard dependencies for the project, a set of
developer-focused dependencies are included.

```shell
pip install -e .[dev]
```

## Configure development tools

This project makes use of the [pre-commit] system. The following applications
are used to lint source code and check formatting:

- [Black] - Python formatter
- [Prettier] - Miscellaneous formatter
- [Ruff] - Python linter

You must initialize the system and install the appropriate hooks. Once
installed, they will be invoked automatically when you commit.

```shell
pre-commit install --install-hooks
```

[pyenv]: https://github.com/pyenv/pyenv
[dev containers]: https://containers.dev/
[pre-commit]: https://pre-commit.com/
[black]: https://black.readthedocs.io/en/stable/index.html
[prettier]: https://prettier.io/
[ruff]: https://beta.ruff.rs/docs/
