"""Fast deterministic dict hashing for deduplication.

Iteratively traverses a nested dict/list/scalar structure using an
explicit stack.  Accumulates a native i64 hash via bit mixing.
Designed to be compiled with mypyc.
"""

from typing import Dict, List

from mypy_extensions import i64


def _hash_to_i64(obj: object) -> i64:
    """Get the Python hash of an object as a native i64."""
    return i64(hash(obj))


def _mix(h: i64, v: i64) -> i64:
    """Murmur-inspired bit mixing using native i64 arithmetic."""
    h = h ^ v
    h = (h << 13) | ((h >> 51) & 0x1FFF)
    h = h * 0x5BD1E995
    return h


def dict_hash(d: Dict[object, object]) -> int:
    """Deterministic hash of a nested dict — full values."""
    h: i64 = 0
    stack: List[object] = [d]

    while stack:
        item: object = stack.pop()

        if item is None:
            h = _mix(h, 7)
        elif isinstance(item, bool):
            h = _mix(h, 1 if item else 2)
        elif isinstance(item, int):
            h = _mix(h, _hash_to_i64(item))
        elif isinstance(item, float):
            h = _mix(h, _hash_to_i64(item))
        elif isinstance(item, str):
            h = _mix(h, _hash_to_i64(item))
            h = _mix(h, i64(len(item)))
        elif isinstance(item, dict):
            keys: List[object] = sorted(item)
            n: i64 = i64(len(keys))
            h = _mix(h, n)
            i: i64 = n - 1
            while i >= 0:
                k: object = keys[i]
                h = _mix(h, _hash_to_i64(k))
                stack.append(item[k])
                i -= 1
        elif isinstance(item, list):
            n = i64(len(item))
            h = _mix(h, n)
            i = n - 1
            while i >= 0:
                stack.append(item[i])
                i -= 1
        else:
            h = _mix(h, _hash_to_i64(item))

    return int(h)


def shape_hash(d: Dict[object, object]) -> int:
    """Deterministic hash of a nested dict — shape only.

    Hashes keys and value types but ignores string/int/float content.
    Two dicts with the same structure always produce the same
    jsonschema validation result, so this is safe for dedup.
    """
    h: i64 = 0
    stack: List[object] = [d]

    while stack:
        item: object = stack.pop()

        if item is None:
            h = _mix(h, 7)
        elif isinstance(item, bool):
            h = _mix(h, 11 if item else 13)
        elif isinstance(item, int):
            h = _mix(h, 17)
        elif isinstance(item, float):
            h = _mix(h, 19)
        elif isinstance(item, str):
            h = _mix(h, 23)
        elif isinstance(item, dict):
            h = _mix(h, 29)
            keys: List[object] = sorted(item)
            n: i64 = i64(len(keys))
            h = _mix(h, n)
            i: i64 = n - 1
            while i >= 0:
                k: object = keys[i]
                h = _mix(h, _hash_to_i64(k))
                stack.append(item[k])
                i -= 1
        elif isinstance(item, list):
            h = _mix(h, 31)
            n = i64(len(item))
            h = _mix(h, n)
            i = n - 1
            while i >= 0:
                stack.append(item[i])
                i -= 1
        else:
            h = _mix(h, 37)

    return int(h)
