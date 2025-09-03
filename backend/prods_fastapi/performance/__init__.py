"""
Performance Optimization Module

This module provides comprehensive performance optimizations for the AI Fashion backend:

1. Database Connection Pooling - Efficient connection management with monitoring
2. Image Optimization - Smart image processing for faster analysis
3. Advanced Caching - Redis-backed caching with cache warming
4. Request Timeouts - Prevent hanging requests
5. Response Compression - Reduce bandwidth usage
6. Performance Monitoring - Real-time performance metrics

Usage:
    from performance import init_performance_systems, get_db_pool, get_cache_manager
    
    # Initialize all performance systems
    await init_performance_systems(app)
"""

from .connection_pool import (
    DatabaseConnectionPool,
    get_db_pool,
    init_db_pool,
    close_db_pool
)

from .image_optimizer import (
    ImageOptimizer,
    OptimizationStats,
    get_image_optimizer
)

from .cache_manager import (
    CacheManager,
    CacheStats,
    get_cache_manager,
    init_cache_manager,
    close_cache_manager
)

from .middleware import (
    RequestTimeoutMiddleware,
    PerformanceMonitoringMiddleware,
    SmartCompressionMiddleware,
    RequestSizeLimitMiddleware,
    add_performance_middleware
)

import logging

logger = logging.getLogger(__name__)

def add_performance_middleware_early(app):
    """
    Add performance middleware before application startup
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Adding performance middleware...")
    
    try:
        # Add performance middleware
        add_performance_middleware(app)
        logger.info("✓ Performance middleware added")
        
    except Exception as e:
        logger.error(f"Failed to add performance middleware: {e}")
        raise

async def init_performance_systems(app):
    """
    Initialize performance systems for the FastAPI application (excluding middleware)
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Initializing performance systems...")
    
    try:
        # Initialize database connection pool
        db_pool = await init_db_pool()
        app.state.db_pool = db_pool
        logger.info("✓ Database connection pool initialized")
        
        # Initialize cache manager
        cache_manager = await init_cache_manager()
        app.state.cache_manager = cache_manager
        logger.info("✓ Cache manager initialized")
        
        # Initialize image optimizer
        image_optimizer = get_image_optimizer()
        app.state.image_optimizer = image_optimizer
        logger.info("✓ Image optimizer initialized")
        
        logger.info("🚀 Performance systems initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize performance systems: {e}")
        raise

async def cleanup_performance_systems(app):
    """
    Clean up performance systems on application shutdown
    
    Args:
        app: FastAPI application instance
    """
    logger.info("Cleaning up performance systems...")
    
    try:
        # Close database pool
        if hasattr(app.state, 'db_pool'):
            await close_db_pool()
            logger.info("✓ Database pool closed")
        
        # Close cache manager
        if hasattr(app.state, 'cache_manager'):
            await close_cache_manager()
            logger.info("✓ Cache manager closed")
        
        logger.info("🧹 Performance systems cleanup completed")
        
    except Exception as e:
        logger.error(f"Error during performance systems cleanup: {e}")

def get_performance_stats(app) -> dict:
    """
    Get comprehensive performance statistics
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Dictionary containing all performance statistics
    """
    stats = {
        "database": {},
        "cache": {},
        "image_optimization": {},
        "requests": {}
    }
    
    try:
        # Database stats
        if hasattr(app.state, 'db_pool'):
            stats["database"] = app.state.db_pool.get_pool_stats()
        
        # Cache stats
        if hasattr(app.state, 'cache_manager'):
            stats["cache"] = app.state.cache_manager.get_cache_stats()
        
        # Image optimization stats
        if hasattr(app.state, 'image_optimizer'):
            stats["image_optimization"] = app.state.image_optimizer.get_optimization_stats()
        
        # Request performance stats
        if hasattr(app.state, 'performance_middleware'):
            stats["requests"] = app.state.performance_middleware.get_stats()
        
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        stats["error"] = str(e)
    
    return stats

__all__ = [
    'DatabaseConnectionPool',
    'get_db_pool',
    'init_db_pool',
    'close_db_pool',
    'ImageOptimizer',
    'OptimizationStats',
    'get_image_optimizer',
    'CacheManager',
    'CacheStats',
    'get_cache_manager',
    'init_cache_manager',
    'close_cache_manager',
    'RequestTimeoutMiddleware',
    'PerformanceMonitoringMiddleware',
    'SmartCompressionMiddleware',
    'RequestSizeLimitMiddleware',
    'add_performance_middleware',
    'add_performance_middleware_early',
    'init_performance_systems',
    'cleanup_performance_systems',
    'get_performance_stats'
]
