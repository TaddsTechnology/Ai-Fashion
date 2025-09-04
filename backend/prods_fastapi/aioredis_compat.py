"""
Compatibility module for aioredis with Python 3.11+

This module handles the TimeoutError duplicate base class issue
that occurs when importing aioredis 2.0.1 with Python 3.11+.
"""

import sys
import asyncio
import builtins


def patch_asyncio_for_aioredis():
    """
    Patch asyncio.TimeoutError to fix aioredis compatibility with Python 3.11+
    
    In Python 3.11+, asyncio.TimeoutError is an alias for builtins.TimeoutError,
    which causes a "duplicate base class" error in aioredis 2.0.1's exception hierarchy.
    """
    if sys.version_info >= (3, 11):
        # Store the original TimeoutError
        original_timeout_error = asyncio.TimeoutError
        
        # Create a unique TimeoutError class that inherits from builtins.TimeoutError
        # but is not the same object
        class AsyncioTimeoutError(builtins.TimeoutError):
            """Unique TimeoutError class for aioredis compatibility"""
            pass
        
        # Replace asyncio.TimeoutError temporarily
        asyncio.TimeoutError = AsyncioTimeoutError
        
        return original_timeout_error
    
    return None


def restore_asyncio_timeout_error(original_timeout_error):
    """Restore the original asyncio.TimeoutError"""
    if original_timeout_error is not None:
        asyncio.TimeoutError = original_timeout_error


# Apply the patch immediately when this module is imported
_original_timeout_error = patch_asyncio_for_aioredis()

# Import aioredis with the patch applied
try:
    import aioredis
    # Store a reference to the successfully imported aioredis
    _aioredis = aioredis
except Exception as e:
    print(f"Warning: Failed to import aioredis even with compatibility patch: {e}")
    _aioredis = None
finally:
    # Restore the original TimeoutError
    restore_asyncio_timeout_error(_original_timeout_error)

# Re-export aioredis
if _aioredis:
    # Export all aioredis components
    Redis = _aioredis.Redis
    StrictRedis = _aioredis.StrictRedis
    from_url = _aioredis.from_url
    ConnectionPool = _aioredis.ConnectionPool
    
    # Export the entire module for compatibility
    aioredis = _aioredis
else:
    # Provide fallback/dummy implementations if needed
    class DummyRedis:
        """Dummy Redis class when aioredis is not available"""
        def __init__(self, *args, **kwargs):
            raise ImportError("aioredis is not available due to compatibility issues")
    
    Redis = DummyRedis
    StrictRedis = DummyRedis
    from_url = lambda *args, **kwargs: DummyRedis()
    ConnectionPool = DummyRedis
    aioredis = None
