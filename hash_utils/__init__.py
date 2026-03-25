"""Fast deterministic dict hashing via mypyc."""

from importlib.metadata import version

from hash_utils._core import dict_hash, shape_hash
from hash_utils._fnv64 import fnv64  # type: ignore[import-not-found]

__version__ = version("fast-hash-utils")
__all__ = ["dict_hash", "fnv64", "shape_hash"]
