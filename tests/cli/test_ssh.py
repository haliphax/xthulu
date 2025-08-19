"""SSH CLI tests"""

# stdlib
from unittest.mock import AsyncMock, Mock, patch

# 3rd party
from click.testing import CliRunner
import pytest

# local
from xthulu import locks
from xthulu.cli import cli
from xthulu.cli.ssh import cli as ssh_cli


@pytest.fixture(autouse=True)
def mock_resources():
    with patch("xthulu.locks.Resources") as p:
        yield p


@pytest.fixture(autouse=True)
def clear_locks():
    locks._Locks.locks.clear()
    yield
    locks._Locks.locks.clear()


@pytest.fixture(autouse=True)
def mock_loop():
    with patch("xthulu.cli.ssh.get_event_loop") as p:
        yield p.return_value


def test_cli_includes_group():
    """The CLI module should include the 'ssh' command group."""

    # act
    command = cli.get_command(Mock(), "ssh")

    # assert
    assert command is not None


@pytest.mark.parametrize("command_name", ["start"])
def test_cli_includes_commands(command_name: str):
    """The command group should include the specified command."""

    # act
    commands = ssh_cli.list_commands(Mock())

    # assert
    assert command_name in commands


@patch("xthulu.cli.ssh.start_server")
def test_start(mock_start: AsyncMock, *, mock_loop: Mock):
    """The 'ssh start' command should start an SSH server in the event loop."""

    # arrange
    mock_loop.run_until_complete = Mock(return_value=mock_start)
    mock_loop.run_forever = Mock(side_effect=KeyboardInterrupt())

    # act
    CliRunner().invoke(cli, ["ssh", "start"], catch_exceptions=False)

    # assert
    mock_start.assert_called_once()
    mock_loop.run_until_complete.assert_called_once()


@patch("xthulu.cli.ssh.start_server")
def test_shutdown(mock_start: AsyncMock, *, mock_loop: Mock):
    """The 'ssh start' command should run lifespan function on shutdown."""

    # arrange
    locks._Locks.locks = {"test_name": {"test_lock": Mock()}}
    CliRunner().invoke(cli, ["ssh", "start"], catch_exceptions=False)
    shutdown = mock_loop.add_signal_handler.call_args_list[0].args[1]

    # act
    shutdown()

    # assert
    mock_loop.stop.assert_called_once()
    assert "test_name" not in locks._Locks.locks
