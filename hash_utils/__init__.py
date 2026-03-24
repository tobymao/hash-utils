"""Fast deterministic dict hashing via mypyc."""

from hash_utils._core import dict_hash, shape_hash

__version__ = "0.1.0"
__all__ = ["dict_hash", "shape_hash"]
