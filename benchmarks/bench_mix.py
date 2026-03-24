"""Compare Murmur vs FNV-1a mixing functions for dict hashing."""

import importlib
import importlib.util
import os
import shutil
import statistics
import sys
import tempfile
import time

from mypyc.build import mypycify
from setuptools import Distribution
from setuptools.command.build_ext import build_ext

N = 10_000

CORE_TEMPLATE = '''\
from typing import Dict, List
from mypy_extensions import i64

_TAG_NONE: i64 = 7
_TAG_BOOL_T: i64 = 11
_TAG_BOOL_F: i64 = 13
_TAG_INT: i64 = 17
_TAG_FLOAT: i64 = 19
_TAG_STR: i64 = 23
_TAG_DICT: i64 = 29
_TAG_LIST: i64 = 31
_TAG_OTHER: i64 = 37

def _hash_to_i64(obj: object) -> i64:
    return i64(hash(obj))

{mix_fn}

def dict_hash(d: Dict[object, object]) -> int:
    h: i64 = 0
    stack: List[object] = [d]
    while stack:
        item: object = stack.pop()
        if item is None:
            h = _mix(h, _TAG_NONE)
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
            h = _mix(h, i64(len(item)))
            keys: List[str] = sorted(item.keys())
            i: i64 = i64(len(keys)) - 1
            while i >= 0:
                k: str = keys[i]
                stack.append(item[k])
                stack.append(k)
                i -= 1
        elif isinstance(item, list):
            h = _mix(h, i64(len(item)))
            i = i64(len(item)) - 1
            while i >= 0:
                stack.append(item[i])
                i -= 1
        else:
            h = _mix(h, _hash_to_i64(item))
    return int(h)

def shape_hash(d: Dict[object, object]) -> int:
    h: i64 = 0
    stack: List[object] = [d]
    while stack:
        item: object = stack.pop()
        if item is None:
            h = _mix(h, _TAG_NONE)
        elif isinstance(item, bool):
            h = _mix(h, _TAG_BOOL_T if item else _TAG_BOOL_F)
        elif isinstance(item, int):
            h = _mix(h, _TAG_INT)
        elif isinstance(item, float):
            h = _mix(h, _TAG_FLOAT)
        elif isinstance(item, str):
            h = _mix(h, _TAG_STR)
        elif isinstance(item, dict):
            h = _mix(h, _TAG_DICT)
            h = _mix(h, i64(len(item)))
            keys: List[str] = sorted(item.keys())
            i: i64 = i64(len(keys)) - 1
            while i >= 0:
                k: str = keys[i]
                h = _mix(h, _hash_to_i64(k))
                stack.append(item[k])
                i -= 1
        elif isinstance(item, list):
            h = _mix(h, _TAG_LIST)
            h = _mix(h, i64(len(item)))
            i = i64(len(item)) - 1
            while i >= 0:
                stack.append(item[i])
                i -= 1
        else:
            h = _mix(h, _TAG_OTHER)
    return int(h)
'''

MIX_MURMUR = '''\
def _mix(h: i64, v: i64) -> i64:
    """Murmur-inspired bit mixing."""
    h = h ^ v
    h = (h << 13) | ((h >> 51) & 0x1FFF)
    h = h * 0x5BD1E995
    return h'''

MIX_FNV1A = '''\
_FNV_PRIME: i64 = 0x100000001B3

def _mix(h: i64, v: i64) -> i64:
    """FNV-1a inspired mixing."""
    h = h ^ v
    h = h * _FNV_PRIME
    return h'''

MIX_DJB2 = '''\
def _mix(h: i64, v: i64) -> i64:
    """DJB2-inspired: shift + add."""
    h = ((h << 5) + h) ^ v
    return h'''

MIX_XXHASH = '''\
def _mix(h: i64, v: i64) -> i64:
    """xxHash-inspired: multiply + xor-shift."""
    h = (h + v) * 0x5BD1E9955BD1E995
    h = h ^ (h >> 27)
    return h'''

MIX_SPLITMIX = '''\
def _mix(h: i64, v: i64) -> i64:
    """Splitmix64-inspired."""
    h = h + v
    h = h ^ (h >> 30)
    h = h * 0x27D4EB2F165B7
    return h'''

MIX_XORSHIFT = '''\
def _mix(h: i64, v: i64) -> i64:
    """Simple xor-shift-multiply."""
    h = h ^ v
    h = h ^ (h >> 16)
    h = h * 0x45D9F3B
    return h'''


def compile_and_load(name: str, mix_fn: str, tmpdir: str):
    """Write, compile with mypyc, and import."""
    src = CORE_TEMPLATE.format(mix_fn=mix_fn)
    filepath = os.path.join(tmpdir, f"{name}.py")
    with open(filepath, "w") as f:
        f.write(src)

    orig_dir = os.getcwd()
    os.chdir(tmpdir)
    try:
        ext_modules = mypycify([filepath], opt_level="3")
        dist = Distribution({"ext_modules": ext_modules})
        cmd = build_ext(dist)
        cmd.inplace = True
        cmd.ensure_finalized()
        cmd.run()
    finally:
        os.chdir(orig_dir)

    sys.path.insert(0, tmpdir)
    try:
        return importlib.import_module(name)
    finally:
        sys.path.pop(0)


def load_pure(name: str, mix_fn: str, tmpdir: str):
    """Write and load as pure Python."""
    src = CORE_TEMPLATE.format(mix_fn=mix_fn)
    filepath = os.path.join(tmpdir, f"{name}.py")
    with open(filepath, "w") as f:
        f.write(src)

    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_dicts(n: int) -> list[dict]:
    return [
        {
            "name": f"test_node_{i}",
            "unique_id": f"project.model.{i}",
            "description": f"A test node for benchmarking purposes #{i}",
            "config": {
                "enabled": True,
                "severity": "ERROR",
                "warn_if": "!= 0",
                "error_if": "> 10",
                "tags": ["ci", "nightly"],
                "meta": {"owner": "team-data", "priority": i % 5},
            },
            "columns": {
                "id": {"type": "integer", "nullable": False},
                "name": {"type": "string", "nullable": True},
                "value": {"type": "float", "nullable": True},
            },
        }
        for i in range(n)
    ]


def bench(name: str, fn, dicts: list[dict], rounds: int = 3) -> float:
    for d in dicts[:100]:
        fn(d)

    times = []
    for _ in range(rounds):
        start = time.perf_counter()
        for d in dicts:
            fn(d)
        times.append(time.perf_counter() - start)

    elapsed = statistics.median(times)
    ops = len(dicts) / elapsed
    print(f"{name:40s}  {elapsed:.4f}s  {ops:>10,.0f} ops/s")
    return elapsed


def check_collisions(name: str, fn, dicts: list[dict]) -> int:
    hashes = [fn(d) for d in dicts]
    unique = len(set(hashes))
    collisions = len(hashes) - unique
    rate = collisions / len(hashes) * 100
    print(f"  {name:12s}  {collisions:>5d} / {len(hashes):>5d}  ({rate:.2f}%)")
    return collisions


VARIANTS = [
    ("murmur", MIX_MURMUR),
    ("fnv1a", MIX_FNV1A),
    ("djb2", MIX_DJB2),
    ("xxhash", MIX_XXHASH),
    ("splitmix", MIX_SPLITMIX),
    ("xorshift", MIX_XORSHIFT),
]


def main() -> None:
    dicts = make_dicts(N)

    with tempfile.TemporaryDirectory() as tmpdir:
        pure_dir = os.path.join(tmpdir, "pure")
        compiled_dir = os.path.join(tmpdir, "compiled")
        os.makedirs(pure_dir)
        os.makedirs(compiled_dir)

        pure_mods = {}
        compiled_mods = {}

        print("Loading pure Python variants...")
        for name, mix_fn in VARIANTS:
            pure_mods[name] = load_pure(f"{name}_pure", mix_fn, pure_dir)

        print("Compiling mypyc variants (-O3)...")
        for name, mix_fn in VARIANTS:
            compiled_mods[name] = compile_and_load(f"{name}_c", mix_fn, compiled_dir)

        print(f"\nBenchmarking {N:,} nested dicts (median of 3 rounds)\n")
        print(f"{'Method':40s}  {'Time':>7s}  {'Throughput':>12s}")
        print("-" * 66)

        for name, _ in VARIANTS:
            bench(f"dict_hash  ({name}, pure python)", pure_mods[name].dict_hash, dicts)
        print()
        for name, _ in VARIANTS:
            bench(f"dict_hash  ({name}, mypyc)", compiled_mods[name].dict_hash, dicts)
        print()
        for name, _ in VARIANTS:
            bench(f"shape_hash ({name}, pure python)", pure_mods[name].shape_hash, dicts)
        print()
        for name, _ in VARIANTS:
            bench(f"shape_hash ({name}, mypyc)", compiled_mods[name].shape_hash, dicts)

        # Collision tests
        print(f"\n{'':14s}  {'collisions':>13s}")

        print("\ndict_hash — 10K distinct nested dicts:")
        for name, _ in VARIANTS:
            check_collisions(name, pure_mods[name].dict_hash, dicts)

        similar = [{"a": i, "b": "same", "c": [1, 2]} for i in range(N)]
        print("\ndict_hash — 10K dicts differing by one int:")
        for name, _ in VARIANTS:
            check_collisions(name, pure_mods[name].dict_hash, similar)

        prefixed = [{"key": f"value_{i}"} for i in range(N)]
        print("\ndict_hash — 10K dicts differing by one string:")
        for name, _ in VARIANTS:
            check_collisions(name, pure_mods[name].dict_hash, prefixed)

        small = [{chr(65 + (i % 26)): i} for i in range(N)]
        print("\ndict_hash — 10K dicts with rotating single-char keys:")
        for name, _ in VARIANTS:
            check_collisions(name, pure_mods[name].dict_hash, small)

        print("\nshape_hash — 10K same-shape dicts (expect all same):")
        for name, _ in VARIANTS:
            shapes = [pure_mods[name].shape_hash(d) for d in dicts]
            unique = len(set(shapes))
            print(f"  {name:12s}  {unique:>5d} unique shapes (should be 1)")


if __name__ == "__main__":
    main()
