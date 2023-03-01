"""Redis cache binding tests"""

# stdlib
from unittest import TestCase
from unittest.mock import Mock, patch

# target
from xthulu.configuration.default import default_config


class TestCacheBinding(TestCase):

    """Test that the Redis cache is bound according to configuration."""

    test_config = {
        **default_config,
        **{"cache": {"host": "test", "port": 123}},
    }
    """Configuration to use during testing"""

    @patch("xthulu.config", test_config)
    @patch("xthulu.Redis")
    def test_binding(self, mock_redis: Mock):
        """Test that the host and port are used when binding the connection."""

        from xthulu import bind_redis

        bind_redis()

        cache_config = self.test_config["cache"]
        mock_redis.assert_called_once_with(
            host=cache_config["host"], port=int(cache_config["port"])
        )
