"""Benchmarks for dict_hash and shape_hash (pure Python vs mypyc)."""

import json
import time

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



if __name__ == "__main__":
    main()
