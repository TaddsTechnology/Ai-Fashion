"""
Redis Cache Manager for AI Fashion Backend
Handles caching of expensive computations, image processing results, and database queries.
"""

import redis
import json
import pickle
import hashlib
import logging
from typing import Any, Optional, Dict, List
from functools import wraps
import asyncio
from datetime import timedelta
import os

# Import aioredis directly
try:
    import aioredis
except ImportError:
    aioredis = None

logger = logging.getLogger(__name__)

# Import configuration
try:
    from config import settings
    REDIS_URL = settings.redis_url
    REDIS_MAX_CONNECTIONS = settings.redis_max_connections
except ImportError:
    # Fallback if config is not available
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))

class CacheManager:
    """Redis-based cache manager with async support"""
    
    def __init__(self):
        self.redis_client = None
        self.async_redis = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connections with fallback"""
        try:
            # Synchronous Redis client with SSL support
            connection_kwargs = {
                "max_connections": REDIS_MAX_CONNECTIONS,
                "decode_responses": False,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
                "retry_on_timeout": True
            }
            
            # Add SSL configuration if using rediss://
            if REDIS_URL.startswith("rediss://"):
                connection_kwargs["ssl"] = True
                connection_kwargs["ssl_cert_reqs"] = None
            
            self.redis_client = redis.from_url(REDIS_URL, **connection_kwargs)
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            self.redis_client = None
            # Initialize in-memory fallback cache
            self._memory_cache = {}
            self._memory_cache_expiry = {}
    
    async def get_async_redis(self):
        """Get async Redis connection"""
        if not aioredis:
            logger.warning("aioredis not available, async operations will be skipped")
            return None
            
        if self.async_redis is None:
            try:
                self.async_redis = await aioredis.from_url(
                    REDIS_URL,
                    max_connections=REDIS_MAX_CONNECTIONS,
                    decode_responses=False
                )
                logger.info("Async Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to async Redis: {e}")
                return None
        return self.async_redis
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key from function arguments"""
        # Create a string representation of all arguments
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        # Hash it to ensure consistent key length
        return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set a value in cache with expiration"""
        if not self.redis_client:
            return False
        
        try:
            # Serialize value
            serialized_value = pickle.dumps(value)
            result = self.redis_client.setex(key, expire_seconds, serialized_value)
            return result
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        if not self.redis_client:
            return None
        
        try:
            serialized_value = self.redis_client.get(key)
            if serialized_value is None:
                return None
            return pickle.loads(serialized_value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def aset(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Async set a value in cache"""
        redis_client = await self.get_async_redis()
        if not redis_client:
            return False
        
        try:
            serialized_value = pickle.dumps(value)
            await redis_client.setex(key, expire_seconds, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Async cache set error: {e}")
            return False
    
    async def aget(self, key: str) -> Optional[Any]:
        """Async get a value from cache"""
        redis_client = await self.get_async_redis()
        if not redis_client:
            return None
        
        try:
            serialized_value = await redis_client.get(key)
            if serialized_value is None:
                return None
            return pickle.loads(serialized_value)
        except Exception as e:
            logger.error(f"Async cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.redis_client:
            return False
        
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache flush pattern error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"error": str(e)}

# Global cache manager instance
cache_manager = CacheManager()

def cached(expire_seconds: int = 3600, key_prefix: str = "default"):
    """
    Decorator to cache function results
    
    Args:
        expire_seconds: Cache expiration time in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_cache_key(
                f"{key_prefix}:{func.__name__}", *args, **kwargs
            )
            
            # Try to get from cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.info(f"Cache miss for {func.__name__}, executing function")
            result = func(*args, **kwargs)
            
            # Cache the result
            cache_manager.set(cache_key, result, expire_seconds)
            return result
        
        return wrapper
    return decorator

def async_cached(expire_seconds: int = 3600, key_prefix: str = "default"):
    """
    Decorator to cache async function results
    
    Args:
        expire_seconds: Cache expiration time in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_cache_key(
                f"{key_prefix}:{func.__name__}", *args, **kwargs
            )
            
            # Try to get from cache first
            cached_result = await cache_manager.aget(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.info(f"Cache miss for {func.__name__}, executing function")
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache_manager.aset(cache_key, result, expire_seconds)
            return result
        
        return wrapper
    return decorator

# Specific cache decorators for different use cases
skin_tone_cache = lambda func: cached(expire_seconds=7200, key_prefix="skin_tone")(func)
color_analysis_cache = lambda func: cached(expire_seconds=3600, key_prefix="color_analysis")(func)
product_recommendation_cache = lambda func: cached(expire_seconds=1800, key_prefix="recommendations")(func)
image_processing_cache = lambda func: cached(expire_seconds=7200, key_prefix="image_processing")(func)

# Cache warming functions
def warm_cache_skin_tones():
    """Pre-populate cache with common skin tone mappings"""
    try:
        from color_utils import get_monk_hex_codes
        
        monk_codes = get_monk_hex_codes()
        for monk_id, hex_codes in monk_codes.items():
            cache_key = f"cache:monk_hex:{monk_id}"
            cache_manager.set(cache_key, hex_codes, expire_seconds=86400)  # 24 hours
        
        logger.info("Cache warmed with skin tone data")
    except Exception as e:
        logger.error(f"Failed to warm skin tone cache: {e}")

def warm_cache_color_palettes():
    """Pre-populate cache with color palette data"""
    try:
        from color_utils import get_seasonal_palettes
        
        palettes = get_seasonal_palettes()
        for seasonal_type, palette in palettes.items():
            cache_key = f"cache:palette:{seasonal_type}"
            cache_manager.set(cache_key, palette, expire_seconds=86400)  # 24 hours
        
        logger.info("Cache warmed with color palette data")
    except Exception as e:
        logger.error(f"Failed to warm color palette cache: {e}")

# Cache health check
def check_cache_health() -> Dict[str, Any]:
    """Check cache health and performance"""
    if not cache_manager.redis_client:
        return {"status": "unhealthy", "error": "Redis not connected"}
    
    try:
        # Test basic operations
        test_key = "health_check_test"
        test_value = {"timestamp": "test", "data": [1, 2, 3]}
        
        # Set test
        set_success = cache_manager.set(test_key, test_value, expire_seconds=60)
        if not set_success:
            return {"status": "unhealthy", "error": "Failed to set test value"}
        
        # Get test
        retrieved_value = cache_manager.get(test_key)
        if retrieved_value != test_value:
            return {"status": "unhealthy", "error": "Retrieved value doesn't match"}
        
        # Delete test
        cache_manager.delete(test_key)
        
        # Get stats
        stats = cache_manager.get_stats()
        
        return {
            "status": "healthy",
            "stats": stats,
            "message": "Cache is working properly"
        }
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
