"""Fast deterministic dict hashing for deduplication.

Iteratively traverses a nested dict/list/scalar structure using an
explicit stack.  Accumulates a native i64 hash via bit mixing.
Designed to be compiled with mypyc.
"""

from typing import Callable, Dict, List

from mypy_extensions import i64

from hash_utils._fnv64 import fnv64  # type: ignore[import-not-found]


def _mix(h: i64, v: i64) -> i64:
    """Murmur-inspired bit mixing using native i64 arithmetic."""
    h = h ^ v
    h = (h << 13) | ((h >> 51) & 0x1FFF)
    h = h * 0x5BD1E995
    return h


def dict_hash(d: Dict[object, object]) -> int:
    """Deterministic hash of a nested dict — full values."""
    _f: Callable[[object], int] = fnv64
    h: i64 = 0
    stack: List[object] = [d]

    while stack:
        item: object = stack.pop()

        if item is None:
            h = _mix(h, 7)
        elif isinstance(item, bool):
            h = _mix(h, 1 if item else 2)
        elif isinstance(item, int):
            h = _mix(h, i64(hash(item)))
        elif isinstance(item, float):
            h = _mix(h, i64(hash(item)))
        elif isinstance(item, str):
            h = _mix(h, i64(_f(item)))
        elif isinstance(item, dict):
            h = _mix(h, 29)
            keys: List[object] = sorted(item)
            n: i64 = i64(len(keys))
            i: i64 = n - 1
            while i >= 0:
                k: object = keys[i]
                h = _mix(h, i64(_f(k)))
                stack.append(item[k])
                i -= 1
        elif isinstance(item, list):
            h = _mix(h, 31)
            n = i64(len(item))
            i = n - 1
            while i >= 0:
                stack.append(item[i])
                i -= 1
        else:
            h = _mix(h, i64(_f(item)))

    return int(h)


def shape_hash(d: Dict[object, object]) -> int:
    """Deterministic hash of a nested dict — shape only.

    Hashes keys and value types but ignores string/int/float content.
    Two dicts with the same structure always produce the same
    jsonschema validation result, so this is safe for dedup.
    """
    _f: Callable[[object], int] = fnv64
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
            i: i64 = n - 1
            while i >= 0:
                k: object = keys[i]
                h = _mix(h, i64(_f(k)))
                stack.append(item[k])
                i -= 1
        elif isinstance(item, list):
            h = _mix(h, 31)
            type_mask: i64 = 0
            n = i64(len(item))
            i = n - 1
            while i >= 0:
                el: object = item[i]
                if el is None:
                    type_mask = type_mask | 1
                elif isinstance(el, bool):
                    type_mask = type_mask | 2
                elif isinstance(el, int):
                    type_mask = type_mask | 4
                elif isinstance(el, float):
                    type_mask = type_mask | 8
                elif isinstance(el, str):
                    type_mask = type_mask | 16
                elif isinstance(el, dict):
                    type_mask = type_mask | 32
                    stack.append(el)
                elif isinstance(el, list):
                    type_mask = type_mask | 64
                    stack.append(el)
                else:
                    type_mask = type_mask | 128
                i -= 1
            h = _mix(h, type_mask)
        else:
            h = _mix(h, 37)

    return int(h)
