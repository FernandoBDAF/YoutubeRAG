"""
Tests for data_transform library helpers.

Run with: python -m tests.core.libraries.data_transform.test_helpers
"""

from core.libraries.data_transform import flatten, group_by, deduplicate, merge_dicts


def test_flatten_simple():
    """Test flattening simple nested dict."""
    nested = {"a": {"b": {"c": 1}}}
    result = flatten(nested)
    assert result == {"a.b.c": 1}
    print("✓ Flatten simple nested dict")


def test_flatten_multiple_keys():
    """Test flattening dict with multiple keys at each level."""
    nested = {"a": {"b": 1, "c": 2}, "d": 3}
    result = flatten(nested)
    assert result == {"a.b": 1, "a.c": 2, "d": 3}
    print("✓ Flatten dict with multiple keys")


def test_flatten_custom_separator():
    """Test flattening with custom separator."""
    nested = {"a": {"b": 1}}
    result = flatten(nested, separator="_")
    assert result == {"a_b": 1}
    print("✓ Flatten with custom separator")


def test_group_by_single_key():
    """Test grouping by single key."""
    items = [
        {"type": "A", "val": 1},
        {"type": "A", "val": 2},
        {"type": "B", "val": 3},
    ]
    result = group_by(items, "type")
    assert len(result) == 2
    assert len(result["A"]) == 2
    assert len(result["B"]) == 1
    print("✓ Group by single key")


def test_group_by_preserves_order():
    """Test that grouping preserves item order within groups."""
    items = [
        {"type": "A", "val": 1},
        {"type": "A", "val": 2},
    ]
    result = group_by(items, "type")
    assert result["A"][0]["val"] == 1
    assert result["A"][1]["val"] == 2
    print("✓ Group by preserves order")


def test_deduplicate_simple():
    """Test deduplicating by ID."""
    items = [
        {"id": 1, "val": "a"},
        {"id": 1, "val": "b"},  # Duplicate
        {"id": 2, "val": "c"},
    ]
    result = deduplicate(items, "id")
    assert len(result) == 2
    assert result[0]["val"] == "a"  # Keeps first
    assert result[1]["val"] == "c"
    print("✓ Deduplicate simple list")


def test_deduplicate_no_duplicates():
    """Test deduplicating list with no duplicates."""
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    result = deduplicate(items, "id")
    assert len(result) == 3
    print("✓ Deduplicate with no duplicates")


def test_merge_dicts_shallow():
    """Test shallow merge (dict2 overwrites dict1)."""
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 3, "c": 4}
    result = merge_dicts(d1, d2, deep=False)
    assert result == {"a": 1, "b": 3, "c": 4}
    print("✓ Merge dicts shallow")


def test_merge_dicts_deep():
    """Test deep merge (nested dicts combined)."""
    d1 = {"a": 1, "b": {"c": 2, "d": 3}}
    d2 = {"b": {"d": 4, "e": 5}, "f": 6}
    result = merge_dicts(d1, d2, deep=True)
    assert result == {"a": 1, "b": {"c": 2, "d": 4, "e": 5}, "f": 6}
    print("✓ Merge dicts deep")


def test_merge_dicts_preserves_original():
    """Test that merge doesn't mutate original dicts."""
    d1 = {"a": 1}
    d2 = {"b": 2}
    result = merge_dicts(d1, d2)
    assert d1 == {"a": 1}  # Unchanged
    assert d2 == {"b": 2}  # Unchanged
    print("✓ Merge preserves original dicts")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Data Transform Library ===\n")

    test_flatten_simple()
    test_flatten_multiple_keys()
    test_flatten_custom_separator()
    test_group_by_single_key()
    test_group_by_preserves_order()
    test_deduplicate_simple()
    test_deduplicate_no_duplicates()
    test_merge_dicts_shallow()
    test_merge_dicts_deep()
    test_merge_dicts_preserves_original()

    print("\n✅ All data transform tests passed!")


if __name__ == "__main__":
    run_all_tests()
