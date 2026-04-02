import time
from typing import Any, Dict, Optional, Tuple

class InMemoryCache:
    """
    Simple in-memory cache with TTL support.
    """
    def __init__(self):
        # key -> (value, expiry_timestamp)
        self._cache: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache if it hasn't expired.
        """
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return None
            
        return value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Store a value in the cache with a given TTL (in seconds).
        """
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """
        Explicitly remove a key from the cache.
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """
        Clear all items from the cache.
        """
        self._cache.clear()
