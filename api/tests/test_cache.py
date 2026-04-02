import pytest
import time
from unittest.mock import patch
from api.cache import InMemoryCache

def test_cache_set_get():
    """Verify basic set and get operations."""
    cache = InMemoryCache()
    cache.set("key1", "val1", ttl=10)
    assert cache.get("key1") == "val1"

def test_cache_expiration():
    """Verify that values expire after TTL."""
    cache = InMemoryCache()
    # Mock time.time to simulate passage of time
    with patch("time.time") as mock_time:
        mock_time.return_value = 1000.0
        cache.set("key1", "val1", ttl=10) # Expires at 1010.0
        
        # Still valid at 1005.0
        mock_time.return_value = 1005.0
        assert cache.get("key1") == "val1"
        
        # Expired at 1011.0
        mock_time.return_value = 1011.0
        assert cache.get("key1") is None
        assert "key1" not in cache._cache

def test_cache_delete():
    """Verify explicit deletion."""
    cache = InMemoryCache()
    cache.set("key1", "val1")
    cache.delete("key1")
    assert cache.get("key1") is None

def test_cache_clear():
    """Verify clearing the full cache."""
    cache = InMemoryCache()
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    cache.clear()
    assert cache.get("k1") is None
    assert cache.get("k2") is None
    assert len(cache._cache) == 0

def test_cache_fallback_access():
    """Verify internal access for fallbacks (used in repo fetching)."""
    cache = InMemoryCache()
    cache.set("key1", "val1", ttl=-1) # Already expired
    # get() returns None
    assert cache.get("key1") is None
    # But internal _cache still has it (until pruned by get or manual)
    # Actually get() deletes it if expired. Let's check logic.
    # If we call get(), it deletes it.
    
    cache.set("key2", "val2", ttl=-1)
    # Access directly without pruning
    val, expiry = cache._cache["key2"]
    assert val == "val2"
