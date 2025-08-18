"""Web CLI tests"""

# stdlib
from unittest.mock import Mock, patch

# 3rd party
from click.testing import CliRunner
import pytest

# local
from xthulu.cli import cli
from xthulu.cli.web import cli as web_cli


def test_cli_includes_group():
    """The CLI module should include the 'web' command group."""

    # act
    command = cli.get_command(Mock(), "web")

    # assert
    assert command is not None


@pytest.mark.parametrize("command_name", ["start"])
def test_cli_includes_commands(command_name: str):
    """The command group should include the specified command."""

    # act
    commands = web_cli.list_commands(Mock())

    # assert
    assert command_name in commands


@patch("xthulu.cli.web.start_server")
def test_start(mock_start: Mock):
    """The 'web start' command should call the `start_server` function."""

    # act
    CliRunner().invoke(cli, ["web", "start"], catch_exceptions=False)

    # assert
    mock_start.assert_called_once()
