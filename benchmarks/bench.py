"""Benchmarks for dict_hash and shape_hash (pure Python vs mypyc)."""

import json
import time
import zlib

N = 10_000


def make_dicts(n: int) -> list[dict]:
    """Generate n realistic nested dicts."""
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


def bench(name: str, fn, dicts: list[dict]) -> float:
    # Warmup
    for d in dicts[:100]:
        fn(d)

    start = time.perf_counter()
    for d in dicts:
        fn(d)
    elapsed = time.perf_counter() - start

    ops = len(dicts) / elapsed
    print(f"{name:40s}  {elapsed:.4f}s  {ops:>10,.0f} ops/s")
    return elapsed


def json_hash(d: dict) -> int:
    return hash(json.dumps(d, sort_keys=True))


def main() -> None:
    import hash_utils._core as core_mod

    is_compiled = hasattr(core_mod, "__loader__") and "mypyc" in str(
        getattr(core_mod, "__file__", "")
    )
    # More reliable: compiled modules are .so/.pyd, not .py
    mod_file = getattr(core_mod, "__file__", "")
    is_compiled = mod_file.endswith((".so", ".pyd"))

    dicts = make_dicts(N)
    print(f"Benchmarking {N:,} nested dicts")
    print(f"mypyc compiled: {is_compiled}\n")
    print(f"{'Method':40s}  {'Time':>7s}  {'Throughput':>12s}")
    print("-" * 66)

    # Pure Python versions (import the source directly)
    import importlib
    import importlib.util
    import pathlib

    core_py = pathlib.Path(__file__).resolve().parent.parent / "hash_utils" / "_core.py"
    spec = importlib.util.spec_from_file_location("_core_pure", core_py)
    pure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pure)

    bench("dict_hash (pure python)", pure.dict_hash, dicts)
    bench("shape_hash (pure python)", pure.shape_hash, dicts)

    if is_compiled:
        from hash_utils import dict_hash, shape_hash

        bench("dict_hash (mypyc)", dict_hash, dicts)

    bench("hash(json.dumps(sort_keys=True))", json_hash, dicts)

    if is_compiled:
        bench("shape_hash (mypyc)", shape_hash, dicts)


def bench_fnv64() -> None:
    """Benchmark fnv64 vs dual crc32."""
    import hash_utils._core as core_mod

    mod_file = getattr(core_mod, "__file__", "")
    is_compiled = mod_file.endswith((".so", ".pyd"))

    # Generate byte payloads from the same dicts
    dicts = make_dicts(N)
    payloads = [json.dumps(d, sort_keys=True).encode() for d in dicts]
    total_bytes = sum(len(p) for p in payloads)

    print(f"\nfnv64 Benchmark: {N:,} payloads ({total_bytes / 1024:.0f} KB total)")
    print(f"mypyc compiled: {is_compiled}\n")
    print(f"{'Method':40s}  {'Time':>7s}  {'Throughput':>12s}")
    print("-" * 66)

    def bench_bytes(name: str, fn) -> None:
        for p in payloads[:100]:
            fn(p)
        start = time.perf_counter()
        for p in payloads:
            fn(p)
        elapsed = time.perf_counter() - start
        ops = len(payloads) / elapsed
        print(f"{name:40s}  {elapsed:.4f}s  {ops:>10,.0f} ops/s")

    def dual_crc32(data: bytes) -> str:
        return f"{zlib.crc32(data)}_{zlib.crc32(data, 1)}"

    bench_bytes("2x zlib.crc32 -> str", dual_crc32)

    import importlib.util
    import pathlib

    core_py = pathlib.Path(__file__).resolve().parent.parent / "hash_utils" / "_core.py"
    spec = importlib.util.spec_from_file_location("_core_pure2", core_py)
    pure = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pure)
    bench_bytes("fnv64 (pure python)", pure.fnv64)

    if is_compiled:
        from hash_utils._core import fnv64 as fnv64_mypyc

        bench_bytes("fnv64 (mypyc)", fnv64_mypyc)

    try:
        from hash_utils._fnv64 import fnv64

        bench_bytes("fnv64 (C)", fnv64)
    except ImportError:
        print("fnv64 (C)                                (not built)")


if __name__ == "__main__":
    main()
    bench_fnv64()
