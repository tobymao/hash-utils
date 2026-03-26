"""Benchmarks for dict_hash, shape_hash, and fnv64."""

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


def bench(name: str, fn, items: list) -> float:
    # Warmup
    for d in items[:100]:
        fn(d)

    start = time.perf_counter()
    for d in items:
        fn(d)
    elapsed = time.perf_counter() - start

    ops = len(items) / elapsed
    print(f"{name:40s}  {elapsed:.4f}s  {ops:>10,.0f} ops/s")
    return elapsed


def json_hash(d: dict) -> int:
    return hash(json.dumps(d, sort_keys=True))


def main() -> None:
    from hash_utils import dict_hash, fnv64, shape_hash

    dicts = make_dicts(N)
    print(f"Benchmarking {N:,} nested dicts\n")
    print(f"{'Method':40s}  {'Time':>7s}  {'Throughput':>12s}")
    print("-" * 66)

    bench("dict_hash (mypyc)", dict_hash, dicts)
    bench("shape_hash (mypyc)", shape_hash, dicts)
    bench("hash(json.dumps(sort_keys=True))", json_hash, dicts)

    # fnv64 benchmark
    payloads = [json.dumps(d, sort_keys=True).encode() for d in dicts]
    total_bytes = sum(len(p) for p in payloads)

    print(f"\nfnv64 Benchmark: {N:,} payloads ({total_bytes / 1024:.0f} KB total)\n")
    print(f"{'Method':40s}  {'Time':>7s}  {'Throughput':>12s}")
    print("-" * 66)

    def dual_crc32(data: bytes) -> str:
        return f"{zlib.crc32(data)}_{zlib.crc32(data, 1)}"

    bench("2x zlib.crc32 -> str", dual_crc32, payloads)
    bench("fnv64 (C)", fnv64, payloads)


if __name__ == "__main__":
    main()
