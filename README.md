# hash-utils

Fast deterministic dict hashing via mypyc, plus a 64-bit FNV-1a hash for bytes.

## Functions

- **`dict_hash(d)`** — deterministic hash of a nested dict's full content (keys + values)
- **`shape_hash(d)`** — structural hash that ignores string/int/float values, only hashing keys, value types, bools, and container lengths
- **`fnv64(data)`** — fast 64-bit FNV-1a hash for bytes/bytearray/memoryview (C extension)

## Install

```bash
pip install fast-hash-utils
```

## Usage

```python
from hash_utils import dict_hash, shape_hash, fnv64

d1 = {"name": "alice", "config": {"enabled": True, "tags": []}}
d2 = {"name": "bob",   "config": {"enabled": True, "tags": []}}

# Full content hash — different names produce different hashes
dict_hash(d1) != dict_hash(d2)

# Shape hash — same structure produces same hash
shape_hash(d1) == shape_hash(d2)

# Fast 64-bit hash of bytes
fnv64(b"hello world")
```

## Why

`shape_hash` enables massive deduplication for jsonschema validation. If 13,000 dicts share the same structure but differ only in string values, they collapse to 1 unique shape — skip 12,999 redundant validations.

`fnv64` provides a fast non-cryptographic 64-bit hash for bytes data — 2x faster than dual-crc32, ~2x faster than md5/sha256, with zero expected collisions under 5 billion inputs.

## Performance

Dict hashing compiled via mypyc to native C. `fnv64` is a C extension with zero Python object boxing in the inner loop.

| Method | ops/s | Notes |
|---|---|---|
| `fnv64` (C) | 1,750K | 64-bit, raw byte buffer |
| `2x zlib.crc32 → str` | 950K | 64-bit via concatenation |
| `shape_hash` (mypyc) | 390K | nested dict structure |
| `dict_hash` (mypyc) | 340K | nested dict full content |
| `json.dumps + hash` | 115K | stdlib baseline |

## Development

```bash
python -m venv .venv && source .venv/bin/activate
make install    # editable install with dev deps
make test       # run tests (pure Python or compiled)
make bench      # run benchmarks
make style      # ruff check --fix + format
make clean      # remove build artifacts
```

## License

MIT
