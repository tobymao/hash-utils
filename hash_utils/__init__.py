"""Fast deterministic dict hashing via mypyc."""

from importlib.metadata import version

from hash_utils._core import dict_hash, shape_hash

__version__ = version("fast-hash-utils")
__all__ = ["dict_hash", "shape_hash"]
