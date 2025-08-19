"""Database CLI tests"""

# stdlib
from unittest.mock import AsyncMock, Mock, patch

# 3rd party
from click.testing import CliRunner
import pytest
from sqlmodel import SQLModel

# local
from xthulu.cli import cli
from xthulu.cli.db import cli as db_cli


@pytest.fixture
def mock_conn():
    with patch("xthulu.cli.db.Resources") as p:
        conn = AsyncMock()
        p.return_value.db.begin.return_value.__aenter__.return_value = conn
        yield conn


@pytest.fixture
def mock_session():
    with patch("xthulu.cli.db.db_session") as p:
        yield p.return_value.__aenter__.return_value


def test_cli_includes_group():
    """The CLI module should include the 'db' command group."""

    # act
    command = cli.get_command(Mock(), "db")

    # assert
    assert command is not None


@pytest.mark.parametrize("command_name", ["create", "destroy", "seed"])
def test_cli_includes_commands(command_name: str):
    """The command group should include the specified command."""

    # act
    commands = db_cli.list_commands(Mock())

    # assert
    assert command_name in commands


@pytest.mark.parametrize("seed", [False, True])
def test_create(seed: bool, mock_conn: Mock, mock_session: Mock):
    """The 'db create' command should create all model tables."""

    # arrange
    from xthulu import models  # noqa: F401

    args = ["db", "create"]

    if seed:
        args.append("-s")

    # act
    CliRunner().invoke(cli, args, catch_exceptions=False)

    # assert
    mock_conn.run_sync.assert_awaited_once_with(SQLModel.metadata.create_all)

    if seed:
        mock_session.commit.assert_awaited()


@pytest.mark.parametrize("is_confirmed", [False, True])
@patch("xthulu.cli.db.confirm")
def test_destroy(mock_confirm: Mock, is_confirmed: bool, mock_conn: Mock):
    """The 'db destroy' command should destroy all model tables."""

    # arrange
    try:
        from userland import models as user_models  # noqa: F401
    except ImportError:
        pass

    mock_confirm.return_value = is_confirmed

    # act
    CliRunner().invoke(cli, ["db", "destroy"], catch_exceptions=False)

    # assert
    if is_confirmed:
        mock_conn.run_sync.assert_awaited_once_with(SQLModel.metadata.drop_all)
    else:
        assert mock_conn.run_sync.call_count == 0


@patch("xthulu.cli.db.confirm")
def test_destroy_force(mock_confirm: Mock, mock_conn: Mock):
    """The 'db destroy --yes' command should not ask for confirmation."""

    # arrange
    try:
        from userland import models as user_models  # noqa: F401
    except ImportError:
        pass

    # act
    CliRunner().invoke(cli, ["db", "destroy", "--yes"], catch_exceptions=False)

    # assert
    mock_conn.run_sync.assert_awaited_once_with(SQLModel.metadata.drop_all)
    mock_confirm.assert_not_called()


def test_seed(mock_session: Mock):
    """The 'db seed' command should import example records."""

    # act
    CliRunner().invoke(cli, ["db", "seed"], catch_exceptions=False)

    # assert
    mock_session.commit.assert_awaited()
