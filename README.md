# hash-utils

Fast deterministic dict hashing via mypyc, plus a 64-bit FNV-1a hash for strings and bytes.

All hashing is **deterministic across processes** — immune to `PYTHONHASHSEED` randomization.

## Functions

- **`dict_hash(d)`** — deterministic hash of a nested dict's full content (keys + values)
- **`shape_hash(d)`** — structural hash that ignores string/int/float values, only hashing keys, value types, and bools
- **`fnv64(data)`** — fast 64-bit FNV-1a hash for str/bytes/bytearray (C extension)

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

# Fast 64-bit hash for strings and bytes
fnv64(b"hello world")
fnv64("hello world")
```

## Why

`shape_hash` enables massive deduplication for jsonschema validation. If 13,000 dicts share the same structure but differ only in string values, they collapse to 1 unique shape — skip 12,999 redundant validations.

`fnv64` provides a fast non-cryptographic 64-bit hash — 2x faster than dual-crc32, with zero expected collisions under 5 billion inputs. Accepts str (zero-copy UTF-8) and bytes.

## Performance

Dict traversal compiled via mypyc to native C. `fnv64` is a C extension using `PyUnicode_AsUTF8AndSize` for zero-copy string access.

| Method | ops/s | Notes |
|---|---|---|
| `fnv64` (C) | 2,000K | 64-bit, str/bytes |
| `2x zlib.crc32 → str` | 950K | 64-bit via concatenation |
| `shape_hash` (mypyc) | 320K | nested dict structure |
| `dict_hash` (mypyc) | 250K | nested dict full content |
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
