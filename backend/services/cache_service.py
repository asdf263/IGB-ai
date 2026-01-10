"""
Redis Cache Service Module
Caching layer for feature extraction results
"""
import json
import hashlib
from typing import Any, Optional


class CacheService:
    """Redis-based caching service with fallback to in-memory."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 0):
        self.redis_client = None
        self.memory_cache = {}
        self._init_redis(redis_url, db)
    
    def _init_redis(self, redis_url: str, db: int):
        """Initialize Redis connection."""
        try:
            import redis
            self.redis_client = redis.from_url(redis_url, db=db, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            print(f"Redis not available, using in-memory cache: {e}")
            self.redis_client = None
    
    def generate_key(self, data: Any) -> str:
        """Generate cache key from data."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return f"igb:{hashlib.sha256(serialized.encode()).hexdigest()[:16]}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.memory_cache.get(key)
        except Exception:
            return None
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            serialized = json.dumps(value, default=str)
            if self.redis_client:
                self.redis_client.setex(key, ttl, serialized)
            else:
                self.memory_cache[key] = value
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            return True
        except Exception:
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            if self.redis_client:
                keys = self.redis_client.keys("igb:*")
                if keys:
                    self.redis_client.delete(*keys)
            else:
                self.memory_cache.clear()
            return True
        except Exception:
            return False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if self.redis_client:
            try:
                self.redis_client.ping()
                return True
            except Exception:
                return False
        return False
