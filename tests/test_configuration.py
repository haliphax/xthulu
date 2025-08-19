"""Configuration tests"""

# local
from xthulu.configuration import deep_update


def test_deep_update():
    """
    The `deep_update` function should appropriately modify the target dict.
    """

    # arrange
    target = {
        "root": 1,
        "other_root": 0,
        "nested": {"value": 1, "other_value": 0},
        "other_nested": {"value": 0},
    }
    updates = {"root": 2, "nested": {"value": 2}}
    expected = {
        "root": 2,
        "other_root": 0,
        "nested": {"value": 2, "other_value": 0},
        "other_nested": {"value": 0},
    }

    # act
    result = deep_update(target, updates)

    # assert
    assert result == expected
