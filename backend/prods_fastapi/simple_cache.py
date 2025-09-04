# Simple cache manager for AI Fashion Backend (No Redis dependency)
import logging
from typing import Dict, Any, Optional, Callable
import time
import functools

logger = logging.getLogger(__name__)

class SimpleCacheManager:
    """Simple in-memory cache manager."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._expiry: Dict[str, float] = {}
        self.default_ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            # Check if expired
            if key in self._expiry and time.time() > self._expiry[key]:
                self.delete(key)
                return None
            return self._cache[key].get('value')
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        self._cache[key] = {'value': value, 'created_at': time.time()}
        if ttl:
            self._expiry[key] = time.time() + ttl
        else:
            self._expiry[key] = time.time() + self.default_ttl
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        self._expiry.clear()

# Global cache instance
cache_manager = SimpleCacheManager()

# Skin tone cache
skin_tone_cache: Dict[str, Any] = {}

def cached(ttl: int = 3600):
    """Simple caching decorator."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__}")
            return result
        
        return wrapper
    return decorator

def warm_cache_skin_tones():
    """Warm up skin tone cache."""
    logger.info("Warming up skin tone cache...")
    # Add some sample data
    skin_tone_cache.update({
        'Monk01': {'seasonal_type': 'Light Spring'},
        'Monk02': {'seasonal_type': 'Light Spring'},
        'Monk03': {'seasonal_type': 'Clear Spring'},
        'Monk04': {'seasonal_type': 'Warm Spring'},
        'Monk05': {'seasonal_type': 'Soft Autumn'},
        'Monk06': {'seasonal_type': 'Warm Autumn'},
        'Monk07': {'seasonal_type': 'Deep Autumn'},
        'Monk08': {'seasonal_type': 'Deep Winter'},
        'Monk09': {'seasonal_type': 'Cool Winter'},
        'Monk10': {'seasonal_type': 'Clear Winter'}
    })
    logger.info(f"Skin tone cache warmed with {len(skin_tone_cache)} entries")

def warm_cache_color_palettes():
    """Warm up color palette cache."""
    logger.info("Warming up color palette cache...")
    # This would normally load color palettes from database or files
    cache_manager.set('color_palettes_loaded', True, 7200)  # 2 hours
    logger.info("Color palette cache warmed")
