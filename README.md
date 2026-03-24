# hash-utils

Fast deterministic dict hashing via mypyc.

## Functions

- **`dict_hash(d)`** — deterministic hash of a nested dict's full content (keys + values)
- **`shape_hash(d)`** — structural hash that ignores string/int/float values, only hashing keys, value types, bools, and container lengths

## Install

```bash
pip install hash-utils
```

## Usage

```python
from hash_utils import dict_hash, shape_hash

d1 = {"name": "alice", "config": {"enabled": True, "tags": []}}
d2 = {"name": "bob",   "config": {"enabled": True, "tags": []}}

# Full content hash — different names produce different hashes
dict_hash(d1) != dict_hash(d2)

# Shape hash — same structure produces same hash
shape_hash(d1) == shape_hash(d2)
```

## Why

`shape_hash` enables massive deduplication for jsonschema validation. If 13,000 dicts share the same structure but differ only in string values, they collapse to 1 unique shape — skip 12,999 redundant validations.

## Performance

Compiled via mypyc to native C. ~400K ops/s for nested dicts on a single core.

| Method | ops/s | Deterministic |
|---|---|---|
| `shape_hash` (mypyc) | 445K | Yes |
| `dict_hash` (mypyc) | 405K | Yes |
| `hash(repr())` | 312K | No |
| `json.dumps + hash` | 206K | Yes |

## Development

```bash
python -m venv .venv && source .venv/bin/activate
make install    # editable install with dev deps
make test       # run tests (pure Python or compiled)
make lint       # ruff check + format check
make clean      # remove build artifacts
```

## License

MIT
