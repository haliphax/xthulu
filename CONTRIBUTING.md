# Contributor guide

⚠️ Contribution at this point is not recommended, but isn't necessarily
unwelcome. Please [open an issue] with the `enhancement` label with your
proposed changes before beginning any work in earnest.

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
developer-focused dependencies are included. Some of them are located in the
`dev` optional dependencies bundle from the project's Python package, but others
come from the [node.js] ecosystem.

```shell
pip install -e .[dev]
nodeenv -p
npm install
```

## Configure development tools

### pre-commit

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

### docker-compose

In order to avoid the need to rebuild the service containers' base image each
time you make changes to the source code, you can create an override
configuration for the `docker-compose` stack. This configuration will mount the
live source code directory into the running `ssh` and `web` containers so that
restarting them should be sufficient to pick up any changes.

<details>
<summary>docker/docker-compose.override.yml</summary>

```yaml
version: "3"

services:
  ssh:
    volumes:
      - ./xthulu:/app/xthulu

  web:
    volumes:
      - ./xthulu:/app/xthulu
```

</details>

## Unit tests

### Framework

The project's chosen testing framework is the standard library's own `unittest`.

```shell
python -m unittest     # run all tests
python -m unittest -h  # list test runner options
```

### Testing asynchronous code

The convenience method `run_coroutine` in the `util` module can be used to await
asynchronous method calls in test cases.

<details>
<summary>Example</summary>

```python
"""Example tests"""

# stdlib
from unittest import TestCase
from unittest.mock import AsyncMock, patch

# local
from xthulu.some_package import some_asynchronous_method
from xthulu.util import run_coroutine


class TestExample(TestCase):

    """Example test case"""

    @patch("xthulu.some_package.a_different_asynchronous_method")
    def test_something_asynchronous(self, mock_method: AsyncMock):
        """Asynchronous method A should await asynchronous method B."""

        result = run_coroutine(some_asynchronous_method())

        assert result == "expected result"
        mock_method.assert_awaited_once()
```

</details>

### Test coverage

The [coverage] application is used to calculate test coverage after unit tests
have been run.

```shell
coverage run --source=xthulu --omit="xthulu/__main__.py" -m unittest
coverage report
```

[open an issue]: https://github.com/haliphax/xthulu/issues/new?labels=enhancement&title=Proposal:%20
[pyenv]: https://github.com/pyenv/pyenv
[dev containers]: https://containers.dev/
[node.js]: https://nodejs.org
[pre-commit]: https://pre-commit.com/
[black]: https://black.readthedocs.io/en/stable/index.html
[prettier]: https://prettier.io/
[ruff]: https://beta.ruff.rs/docs/
[coverage]: https://coverage.readthedocs.io/en/latest/
