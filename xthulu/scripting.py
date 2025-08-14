"""Scripting utilities"""

# stdlib
from importlib.machinery import ModuleSpec, PathFinder
from types import ModuleType

# local
from .configuration import get_config


def load_userland_module(name: str) -> ModuleType | None:
    """Load module from userland scripts"""

    pathfinder = PathFinder()
    paths = get_config("ssh.userland.paths")
    split: list[str] = name.split(".")
    found: ModuleSpec | None = None
    mod: ModuleType | None = None

    for seg in split:
        if mod is not None:
            found = pathfinder.find_spec(seg, list(mod.__path__))
        else:
            found = pathfinder.find_spec(seg, paths)

        if found is not None and found.loader is not None:
            mod = found.loader.load_module(found.name)

    return mod
