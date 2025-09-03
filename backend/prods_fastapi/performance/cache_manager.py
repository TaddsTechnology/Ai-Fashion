"""
Advanced Caching System with Cache Warming and Performance Monitoring
"""
import asyncio
import json
import pickle
import time
import hashlib
import logging
from typing import Any, Optional, Dict, List, Callable, Union
from dataclasses import dataclass, asdict
from functools import wraps
from contextlib import asynccontextmanager
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
import threading

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_get_time_ms: float = 0.0
    total_set_time_ms: float = 0.0
    avg_get_time_ms: float = 0.0
    avg_set_time_ms: float = 0.0

class CacheManager:
    """Advanced cache manager with Redis backend and in-memory fallback"""
    
    def __init__(self, redis_url: str = None):
        self.stats = CacheStats()
        self.local_cache = {}  # In-memory fallback
        self.cache_locks = {}  # Prevent cache stampede
        self._stats_lock = threading.Lock()
        
        # Redis configuration
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.redis_client = None
        self.redis_available = False
        
        # Cache warming configuration
        self.warm_cache_enabled = True
        self.warming_tasks = []
        
        # Initialize Redis connection
        asyncio.create_task(self._init_redis())
        
    async def _init_redis(self):
        """Initialize Redis connection with fallback"""
        try:
            pool = ConnectionPool.from_url(
                self.redis_url,
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30
            )
            self.redis_client = redis.Redis(connection_pool=pool)
            
            # Test connection
            await self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis cache connection established")
            
            # Start cache warming
            if self.warm_cache_enabled:
                asyncio.create_task(self._warm_cache())
                
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory cache: {e}")
            self.redis_available = False
            self.redis_client = None
    
    def _generate_cache_key(self, key: str, namespace: str = "default") -> str:
        """Generate a standardized cache key"""
        return f"ai_fashion:{namespace}:{key}"
    
    def _hash_complex_key(self, *args, **kwargs) -> str:
        """Generate hash for complex cache keys"""
        key_data = {"args": args, "kwargs": sorted(kwargs.items())}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache with performance tracking"""
        start_time = time.time()
        cache_key = self._generate_cache_key(key, namespace)
        
        try:
            # Try Redis first
            if self.redis_available and self.redis_client:
                try:
                    data = await self.redis_client.get(cache_key)
                    if data:
                        with self._stats_lock:
                            self.stats.hits += 1
                            elapsed = (time.time() - start_time) * 1000
                            self.stats.total_get_time_ms += elapsed
                            self.stats.avg_get_time_ms = self.stats.total_get_time_ms / (self.stats.hits + self.stats.misses)
                        
                        return pickle.loads(data)
                        
                except Exception as e:
                    logger.warning(f"Redis get error: {e}")
                    self.redis_available = False
            
            # Fallback to in-memory cache
            if cache_key in self.local_cache:
                with self._stats_lock:
                    self.stats.hits += 1
                return self.local_cache[cache_key]["value"]
            
            # Cache miss
            with self._stats_lock:
                self.stats.misses += 1
                elapsed = (time.time() - start_time) * 1000
                self.stats.total_get_time_ms += elapsed
                if (self.stats.hits + self.stats.misses) > 0:
                    self.stats.avg_get_time_ms = self.stats.total_get_time_ms / (self.stats.hits + self.stats.misses)
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            with self._stats_lock:
                self.stats.errors += 1
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600, 
        namespace: str = "default"
    ) -> bool:
        """Set value in cache with performance tracking"""
        start_time = time.time()
        cache_key = self._generate_cache_key(key, namespace)
        
        try:
            # Try Redis first
            if self.redis_available and self.redis_client:
                try:
                    data = pickle.dumps(value)
                    await self.redis_client.setex(cache_key, ttl, data)
                    
                    with self._stats_lock:
                        self.stats.sets += 1
                        elapsed = (time.time() - start_time) * 1000
                        self.stats.total_set_time_ms += elapsed
                        self.stats.avg_set_time_ms = self.stats.total_set_time_ms / self.stats.sets
                    
                    return True
                    
                except Exception as e:
                    logger.warning(f"Redis set error: {e}")
                    self.redis_available = False
            
            # Fallback to in-memory cache
            self.local_cache[cache_key] = {
                "value": value,
                "expires_at": time.time() + ttl
            }
            
            with self._stats_lock:
                self.stats.sets += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            with self._stats_lock:
                self.stats.errors += 1
            return False
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from cache"""
        cache_key = self._generate_cache_key(key, namespace)
        
        try:
            # Delete from Redis
            if self.redis_available and self.redis_client:
                try:
                    await self.redis_client.delete(cache_key)
                except Exception as e:
                    logger.warning(f"Redis delete error: {e}")
            
            # Delete from local cache
            if cache_key in self.local_cache:
                del self.local_cache[cache_key]
            
            with self._stats_lock:
                self.stats.deletes += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            with self._stats_lock:
                self.stats.errors += 1
            return False
    
    async def get_or_set(
        self, 
        key: str, 
        fetch_func: Callable, 
        ttl: int = 3600, 
        namespace: str = "default"
    ) -> Any:
        """Get from cache or set if not exists"""
        
        # Check cache first
        cached_value = await self.get(key, namespace)
        if cached_value is not None:
            return cached_value
        
        # Prevent cache stampede with locks
        lock_key = f"lock:{namespace}:{key}"
        if lock_key in self.cache_locks:
            # Wait for other request to complete
            await asyncio.sleep(0.1)
            return await self.get(key, namespace)
        
        try:
            # Set lock
            self.cache_locks[lock_key] = True
            
            # Fetch new value
            if asyncio.iscoroutinefunction(fetch_func):
                value = await fetch_func()
            else:
                value = fetch_func()
            
            # Cache the result
            await self.set(key, value, ttl, namespace)
            
            return value
            
        finally:
            # Remove lock
            if lock_key in self.cache_locks:
                del self.cache_locks[lock_key]
    
    def cache_result(
        self, 
        ttl: int = 3600, 
        namespace: str = "default",
        key_func: Callable = None
    ):
        """Decorator to cache function results"""
        
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{self._hash_complex_key(*args, **kwargs)}"
                
                # Try to get from cache
                cached_result = await self.get(cache_key, namespace)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                await self.set(cache_key, result, ttl, namespace)
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, create an async task
                return asyncio.create_task(async_wrapper(*args, **kwargs))
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    async def _warm_cache(self):
        """Warm cache with frequently accessed data"""
        logger.info("Starting cache warming...")
        
        try:
            # Warm monk skin tone data
            await self._warm_monk_tones()
            
            # Warm color palette data
            await self._warm_color_palettes()
            
            # Warm frequently accessed colors
            await self._warm_popular_colors()
            
            logger.info("Cache warming completed successfully")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
    
    async def _warm_monk_tones(self):
        """Warm cache with Monk skin tone data"""
        try:
            from database import SessionLocal, SkinToneMapping
            
            db = SessionLocal()
            try:
                mappings = db.query(SkinToneMapping).all()
                monk_tones = {}
                
                for mapping in mappings:
                    display_name = mapping.monk_tone.replace('Monk0', 'Monk ').replace('Monk', 'Monk ')
                    if display_name.endswith('10'):
                        display_name = 'Monk 10'
                    monk_tones[display_name] = mapping.hex_code
                
                await self.set("monk_skin_tones", monk_tones, ttl=3600*24, namespace="skin_tone")  # Cache for 24 hours
                logger.debug("Monk skin tones cached")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.warning(f"Failed to warm monk tones cache: {e}")
    
    async def _warm_color_palettes(self):
        """Warm cache with color palette data"""
        try:
            from database import SessionLocal, ColorPalette
            
            db = SessionLocal()
            try:
                palettes = db.query(ColorPalette).all()
                
                for palette in palettes:
                    cache_key = f"color_palette_{palette.skin_tone}"
                    palette_data = {
                        "skin_tone": palette.skin_tone,
                        "flattering_colors": palette.flattering_colors,
                        "colors_to_avoid": palette.colors_to_avoid,
                        "description": palette.description
                    }
                    
                    await self.set(cache_key, palette_data, ttl=3600*12, namespace="color_palette")  # Cache for 12 hours
                
                logger.debug(f"Cached {len(palettes)} color palettes")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.warning(f"Failed to warm color palettes cache: {e}")
    
    async def _warm_popular_colors(self):
        """Warm cache with popular/frequently accessed colors"""
        try:
            from database import SessionLocal
            from sqlalchemy import text
            
            db = SessionLocal()
            try:
                # Get most common colors
                popular_colors_query = text("""
                    SELECT DISTINCT hex_code, color_name, color_family, brightness_level
                    FROM comprehensive_colors 
                    WHERE color_family IN ('blue', 'green', 'red', 'purple', 'neutral', 'brown', 'pink')
                    AND brightness_level IN ('medium', 'dark', 'light')
                    AND hex_code IS NOT NULL
                    AND color_name IS NOT NULL
                    ORDER BY color_name
                    LIMIT 100
                """)
                
                result = db.execute(popular_colors_query)
                popular_colors = result.fetchall()
                
                colors_data = []
                for row in popular_colors:
                    colors_data.append({
                        "hex_code": row[0],
                        "color_name": row[1],
                        "color_family": row[2] or "unknown",
                        "brightness_level": row[3] or "medium"
                    })
                
                await self.set("popular_colors", colors_data, ttl=3600*6, namespace="colors")  # Cache for 6 hours
                logger.debug(f"Cached {len(colors_data)} popular colors")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.warning(f"Failed to warm popular colors cache: {e}")
    
    async def invalidate_namespace(self, namespace: str):
        """Invalidate all cache entries in a namespace"""
        try:
            if self.redis_available and self.redis_client:
                pattern = f"ai_fashion:{namespace}:*"
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            
            # Clear local cache entries
            keys_to_remove = [k for k in self.local_cache.keys() if f":{namespace}:" in k]
            for key in keys_to_remove:
                del self.local_cache[key]
            
            logger.info(f"Invalidated cache namespace: {namespace}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate namespace {namespace}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._stats_lock:
            hit_rate = (self.stats.hits / (self.stats.hits + self.stats.misses)) * 100 if (self.stats.hits + self.stats.misses) > 0 else 0
            
            return {
                "redis_available": self.redis_available,
                "total_operations": self.stats.hits + self.stats.misses + self.stats.sets + self.stats.deletes,
                "hits": self.stats.hits,
                "misses": self.stats.misses,
                "sets": self.stats.sets,
                "deletes": self.stats.deletes,
                "errors": self.stats.errors,
                "hit_rate_percent": round(hit_rate, 2),
                "avg_get_time_ms": round(self.stats.avg_get_time_ms, 2),
                "avg_set_time_ms": round(self.stats.avg_set_time_ms, 2),
                "local_cache_size": len(self.local_cache),
                "active_locks": len(self.cache_locks)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        start_time = time.time()
        
        try:
            # Test Redis connection
            redis_healthy = False
            redis_response_time = None
            
            if self.redis_available and self.redis_client:
                try:
                    redis_start = time.time()
                    await self.redis_client.ping()
                    redis_response_time = (time.time() - redis_start) * 1000
                    redis_healthy = True
                except Exception:
                    redis_healthy = False
            
            # Test local cache
            test_key = "health_check_test"
            test_value = {"timestamp": time.time()}
            
            await self.set(test_key, test_value, ttl=10)
            retrieved_value = await self.get(test_key)
            local_cache_healthy = retrieved_value is not None
            
            # Clean up test data
            await self.delete(test_key)
            
            total_response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy" if (redis_healthy or local_cache_healthy) else "unhealthy",
                "redis_healthy": redis_healthy,
                "redis_response_time_ms": round(redis_response_time, 2) if redis_response_time else None,
                "local_cache_healthy": local_cache_healthy,
                "total_response_time_ms": round(total_response_time, 2),
                "stats": self.get_cache_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round((time.time() - start_time) * 1000, 2)
            }
    
    async def close(self):
        """Close cache connections"""
        if self.redis_client:
            await self.redis_client.close()
        self.local_cache.clear()
        self.cache_locks.clear()
        logger.info("Cache manager closed")

# Global cache manager instance
cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Get or create cache manager instance"""
    global cache_manager
    if cache_manager is None:
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        cache_manager = CacheManager(redis_url)
        logger.info("Cache manager initialized")
    return cache_manager

async def init_cache_manager():
    """Initialize cache manager"""
    global cache_manager
    if cache_manager is None:
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        cache_manager = CacheManager(redis_url)
        logger.info("Async cache manager initialized")
    return cache_manager

async def close_cache_manager():
    """Close cache manager"""
    global cache_manager
    if cache_manager:
        await cache_manager.close()
        cache_manager = None
        logger.info("Cache manager closed")
