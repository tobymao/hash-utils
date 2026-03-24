from __future__ import annotations

from hash_utils import dict_hash, shape_hash


class TestDictHash:
    """Tests for dict_hash — full content hashing."""

    def test_deterministic(self):
        d = {"a": 1, "b": "hello", "c": [1, 2, 3]}
        assert dict_hash(d) == dict_hash(d)

    def test_key_order_independent(self):
        """Sorted keys means insertion order doesn't matter."""
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}
        assert dict_hash(d1) == dict_hash(d2)

    def test_different_values_differ(self):
        d1 = {"a": 1}
        d2 = {"a": 2}
        assert dict_hash(d1) != dict_hash(d2)

    def test_different_keys_differ(self):
        d1 = {"a": 1}
        d2 = {"b": 1}
        assert dict_hash(d1) != dict_hash(d2)

    def test_nested_dicts(self):
        d1 = {"a": {"b": {"c": 1}}}
        d2 = {"a": {"b": {"c": 1}}}
        assert dict_hash(d1) == dict_hash(d2)

    def test_nested_dicts_differ(self):
        d1 = {"a": {"b": {"c": 1}}}
        d2 = {"a": {"b": {"c": 2}}}
        assert dict_hash(d1) != dict_hash(d2)

    def test_lists(self):
        d1 = {"a": [1, 2, 3]}
        d2 = {"a": [1, 2, 3]}
        assert dict_hash(d1) == dict_hash(d2)

    def test_list_order_matters(self):
        d1 = {"a": [1, 2]}
        d2 = {"a": [2, 1]}
        assert dict_hash(d1) != dict_hash(d2)

    def test_empty_dict(self):
        assert dict_hash({}) == dict_hash({})

    def test_none_values(self):
        d1 = {"a": None}
        d2 = {"a": None}
        assert dict_hash(d1) == dict_hash(d2)

    def test_none_vs_zero(self):
        d1 = {"a": None}
        d2 = {"a": 0}
        assert dict_hash(d1) != dict_hash(d2)

    def test_bool_values(self):
        d1 = {"a": True}
        d2 = {"a": False}
        assert dict_hash(d1) != dict_hash(d2)

    def test_float_values(self):
        d1 = {"a": 1.5}
        d2 = {"a": 1.5}
        assert dict_hash(d1) == dict_hash(d2)

    def test_mixed_types(self):
        d = {
            "str": "hello",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, "two", 3.0],
            "dict": {"nested": True},
        }
        assert dict_hash(d) == dict_hash(d)

    def test_string_length_matters(self):
        """Strings with same hash prefix but different length should differ."""
        d1 = {"a": "x"}
        d2 = {"a": "xx"}
        assert dict_hash(d1) != dict_hash(d2)

    def test_int_keys(self):
        d1 = {1: "a", 2: "b"}
        d2 = {1: "a", 2: "b"}
        assert dict_hash(d1) == dict_hash(d2)

    def test_int_keys_differ(self):
        d1 = {1: "a"}
        d2 = {2: "a"}
        assert dict_hash(d1) != dict_hash(d2)

    def test_tuple_keys(self):
        d1 = {(1, 2): "a"}
        d2 = {(1, 3): "a"}
        assert dict_hash(d1) != dict_hash(d2)

    def test_returns_int(self):
        assert isinstance(dict_hash({"a": 1}), int)


class TestShapeHash:
    """Tests for shape_hash — structural hashing."""

    def test_deterministic(self):
        d = {"a": 1, "b": "hello"}
        assert shape_hash(d) == shape_hash(d)

    def test_ignores_string_values(self):
        d1 = {"name": "alice", "city": "london"}
        d2 = {"name": "bob", "city": "paris"}
        assert shape_hash(d1) == shape_hash(d2)

    def test_ignores_int_values(self):
        d1 = {"count": 1, "total": 100}
        d2 = {"count": 999, "total": 0}
        assert shape_hash(d1) == shape_hash(d2)

    def test_ignores_float_values(self):
        d1 = {"score": 1.5}
        d2 = {"score": 99.9}
        assert shape_hash(d1) == shape_hash(d2)

    def test_different_keys_differ(self):
        d1 = {"a": 1}
        d2 = {"b": 1}
        assert shape_hash(d1) != shape_hash(d2)

    def test_bool_values_matter(self):
        d1 = {"enabled": True}
        d2 = {"enabled": False}
        assert shape_hash(d1) != shape_hash(d2)

    def test_different_value_types_differ(self):
        d1 = {"a": "string"}
        d2 = {"a": 42}
        assert shape_hash(d1) != shape_hash(d2)

    def test_dict_length_matters(self):
        d1 = {"a": 1, "b": 2}
        d2 = {"a": 1}
        assert shape_hash(d1) != shape_hash(d2)

    def test_list_length_matters(self):
        d1 = {"items": [1, 2, 3]}
        d2 = {"items": [1]}
        assert shape_hash(d1) != shape_hash(d2)

    def test_nested_shape_same(self):
        """Two dicts with identical structure but different leaf values."""
        d1 = {
            "name": "test_user",
            "config": {"enabled": True, "severity": "ERROR", "tags": []},
        }
        d2 = {
            "name": "other_user",
            "config": {"enabled": True, "severity": "WARNING", "tags": []},
        }
        assert shape_hash(d1) == shape_hash(d2)

    def test_nested_shape_differs(self):
        """Different structure should produce different hashes."""
        d1 = {"config": {"enabled": True}}
        d2 = {"config": {"enabled": True, "extra": "field"}}
        assert shape_hash(d1) != shape_hash(d2)

    def test_empty_dict(self):
        assert shape_hash({}) == shape_hash({})

    def test_none_tagged(self):
        d1 = {"a": None}
        d2 = {"a": "hello"}
        assert shape_hash(d1) != shape_hash(d2)

    def test_key_order_independent(self):
        d1 = {"a": 1, "b": 2}
        d2 = {"b": 2, "a": 1}
        assert shape_hash(d1) == shape_hash(d2)

    def test_int_keys(self):
        d1 = {1: "a", 2: "b"}
        d2 = {1: "x", 2: "y"}
        assert shape_hash(d1) == shape_hash(d2)

    def test_int_keys_differ(self):
        d1 = {1: "a"}
        d2 = {2: "a"}
        assert shape_hash(d1) != shape_hash(d2)

    def test_returns_int(self):
        assert isinstance(shape_hash({"a": 1}), int)

    def test_realistic_dedup(self):
        """Simulate the jsonschema validation dedup use case."""
        # Generate 100 dicts that differ only in string/int values
        dicts = []
        for i in range(100):
            d = {
                "name": f"test_node_{i}",
                "unique_id": f"project.model.{i}",
                "config": {
                    "enabled": True,
                    "severity": "ERROR",
                    "tags": [],
                },
                "columns": {},
            }
            dicts.append(d)

        hashes = {shape_hash(d) for d in dicts}
        assert len(hashes) == 1, f"Expected 1 unique shape, got {len(hashes)}"


class TestDictHashVsShapeHash:
    """Verify the two functions behave differently where expected."""

    def test_dict_hash_distinguishes_values(self):
        d1 = {"a": "hello"}
        d2 = {"a": "world"}
        assert dict_hash(d1) != dict_hash(d2)
        assert shape_hash(d1) == shape_hash(d2)

    def test_both_distinguish_keys(self):
        d1 = {"a": 1}
        d2 = {"b": 1}
        assert dict_hash(d1) != dict_hash(d2)
        assert shape_hash(d1) != shape_hash(d2)

    def test_both_distinguish_structure(self):
        d1 = {"a": [1, 2]}
        d2 = {"a": {"b": 1}}
        assert dict_hash(d1) != dict_hash(d2)
        assert shape_hash(d1) != shape_hash(d2)
