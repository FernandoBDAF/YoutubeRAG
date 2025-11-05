"""
Tests for caching library LRU cache.

Run with: python -m tests.core.libraries.caching.test_lru_cache
"""

import time
from core.libraries.caching import LRUCache, cached


def test_cache_set_get():
    """Test basic cache set and get."""
    cache = LRUCache(max_size=10, name="test")

    cache.set("key1", "value1")
    result = cache.get("key1")

    assert result == "value1"
    assert cache.size() == 1
    print("✓ Cache set/get working")


def test_cache_miss_returns_default():
    """Test cache miss returns default value."""
    cache = LRUCache(max_size=10, name="test")

    result = cache.get("missing_key", default="default_value")

    assert result == "default_value"
    print("✓ Cache miss returns default")


def test_cache_lru_eviction():
    """Test LRU eviction when cache is full."""
    cache = LRUCache(max_size=3, name="test")

    # Fill cache
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    # Access key1 to make it recently used
    cache.get("key1")

    # Add key4 - should evict key2 (least recently used)
    cache.set("key4", "value4")

    assert cache.get("key1") == "value1"  # Still there (recently used)
    assert cache.get("key2") is None  # Evicted (least recently used)
    assert cache.get("key3") == "value3"  # Still there
    assert cache.get("key4") == "value4"  # Newly added
    print("✓ LRU eviction working")


def test_cache_ttl_expiration():
    """Test TTL expiration."""
    cache = LRUCache(max_size=10, ttl=0.5, name="test")  # 0.5 second TTL

    cache.set("key1", "value1")

    # Should be in cache immediately
    assert cache.get("key1") == "value1"

    # Wait for TTL to expire
    time.sleep(0.6)

    # Should be expired
    result = cache.get("key1")
    assert result is None
    print("✓ TTL expiration working")


def test_cache_statistics():
    """Test cache statistics tracking."""
    cache = LRUCache(max_size=10, name="test")

    # Generate some hits and misses
    cache.set("key1", "value1")
    cache.get("key1")  # Hit
    cache.get("key1")  # Hit
    cache.get("missing")  # Miss
    cache.get("missing2")  # Miss

    stats = cache.stats()

    assert stats["hits"] == 2
    assert stats["misses"] == 2
    assert stats["hit_rate"] == 50.0
    assert stats["size"] == 1
    assert stats["max_size"] == 10
    print(
        f"✓ Cache statistics: {stats['hits']} hits, {stats['misses']} misses, {stats['hit_rate']}% hit rate"
    )


def test_cache_clear():
    """Test cache clear."""
    cache = LRUCache(max_size=10, name="test")

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.size() == 2

    cache.clear()

    assert cache.size() == 0
    assert cache.get("key1") is None
    print("✓ Cache clear working")


def test_cached_decorator():
    """Test @cached decorator."""
    call_count = [0]

    @cached(max_size=10, ttl=60)
    def expensive_func(x):
        call_count[0] += 1
        return x * 2

    # First call - should call function
    result1 = expensive_func(5)
    assert result1 == 10
    assert call_count[0] == 1

    # Second call with same arg - should hit cache
    result2 = expensive_func(5)
    assert result2 == 10
    assert call_count[0] == 1  # Not called again!

    # Different arg - should call function
    result3 = expensive_func(10)
    assert result3 == 20
    assert call_count[0] == 2

    print("✓ @cached decorator working")


def test_cached_decorator_with_custom_key():
    """Test @cached decorator with custom key function."""
    call_count = [0]

    @cached(
        max_size=10,
        key_func=lambda user_id, _: f"user_{user_id}",  # Ignore second param
        name="custom_key",
    )
    def get_user(user_id, timestamp):
        call_count[0] += 1
        return f"User {user_id}"

    # Different timestamps, same user_id - should hit cache
    result1 = get_user("123", "2025-01-01")
    result2 = get_user("123", "2025-01-02")

    assert result1 == result2
    assert call_count[0] == 1  # Only called once!

    print("✓ @cached with custom key function working")


def test_cache_update_existing_key():
    """Test updating existing cache key."""
    cache = LRUCache(max_size=10, name="test")

    cache.set("key1", "value1")
    cache.set("key1", "value2")  # Update

    result = cache.get("key1")
    assert result == "value2"
    assert cache.size() == 1  # Still one item
    print("✓ Cache update working")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Caching Library ===\n")

    test_cache_set_get()
    test_cache_miss_returns_default()
    test_cache_lru_eviction()
    test_cache_ttl_expiration()
    test_cache_statistics()
    test_cache_clear()
    test_cached_decorator()
    test_cached_decorator_with_custom_key()
    test_cache_update_existing_key()

    print("\n✅ All caching tests passed!")


if __name__ == "__main__":
    run_all_tests()
