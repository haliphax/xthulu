"""Scripting tests"""

# stdlib
from unittest.mock import Mock, patch

# 3rd party
import pytest

# local
from xthulu.scripting import load_userland_module


@pytest.mark.parametrize(
    ["path", "found"], [["root.good", True], ["root.bad", False]]
)
@patch("xthulu.scripting.PathFinder")
@patch("xthulu.scripting.get_config", return_value=["/test"])
def test_load_userland_module(
    mock_config: Mock, mock_pathfinder: Mock, path: str, found: bool
):
    """The `load_userland_module` method should return the module if found."""

    # arrange
    mock_module = Mock(__path__="")
    mock_found = Mock()
    mock_found.loader.load_module.return_value = mock_module
    mock_pathfinder.return_value.find_spec.side_effect = [
        mock_found if found else None,
        mock_found if found else None,
    ]

    # act
    result = load_userland_module(path)

    # assert
    if found:
        assert result == mock_module
    else:
        assert result is None
