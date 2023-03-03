"""Resources tests"""

# type checking
from typing import Type

# stdlib
from unittest import TestCase
from unittest.mock import Mock, patch

# 3rd party
from apiflask import APIFlask
from gino import Gino
from redis import Redis
from parameterized import parameterized

# target
from xthulu.resources import Resources


class TestResources(TestCase):

    """Resources singleton tests"""

    def setUp(self):
        if hasattr(Resources, "_singleton"):
            del Resources._singleton

    def tearDown(self):
        if hasattr(Resources, "_singleton"):
            del Resources._singleton

    def mock_exists(self):
        return True

    @patch("xthulu.resources.exists", new=mock_exists)
    @patch("xthulu.resources.load")
    def test_config_file_loaded(self, mock_load: Mock):
        Resources()

        mock_load.assert_called_once_with("data/config.toml")

    @patch("xthulu.resources.exists", new=mock_exists)
    @patch("xthulu.resources.environ", new=Mock(get=lambda *_: "test"))
    @patch("xthulu.resources.load")
    def test_config_file_from_env_used(self, mock_load: Mock):
        Resources()

        mock_load.assert_called_once_with("test")

    @parameterized.expand(
        (("app", APIFlask), ("cache", Redis), ("db", Gino)),
    )
    @patch("xthulu.resources.load", new=lambda *_: {})
    @patch("xthulu.resources.exists", new=mock_exists)
    def test_property_assignment(self, name: str, cls: Type):
        resources = Resources()

        assert isinstance(getattr(resources, name), cls)
