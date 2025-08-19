"""Logger tests"""

# stdlib
from unittest.mock import Mock, patch

# local
from xthulu.logger import namer, rotator


def test_namer():
    """Namer should append '.gz' to filenames."""

    # arrange
    original = "test"
    expected = "test.gz"

    # act
    result = namer(original)

    # assert
    assert result == expected


@patch("xthulu.logger.copyfileobj")
@patch("xthulu.logger.remove")
@patch("xthulu.logger.gzip.open")
@patch("xthulu.logger.open")
def test_rotator(mock_open: Mock, mock_gzip: Mock, mock_remove: Mock, *_):
    # act
    rotator("file", "file.tgz")

    # assert
    mock_open.assert_called_once_with("file", "rb")
    mock_gzip.assert_called_once_with("file.tgz", "wb")
