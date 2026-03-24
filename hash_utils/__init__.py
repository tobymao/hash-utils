"""Fast deterministic dict hashing via mypyc."""

from hash_utils._core import dict_hash, shape_hash
from hash_utils._version import __version__
__all__ = ["dict_hash", "shape_hash"]
