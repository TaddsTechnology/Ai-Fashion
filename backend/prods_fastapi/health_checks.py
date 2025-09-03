"""
Health Check Functions for AI Fashion Backend Dependencies

Provides specific health check implementations for:
- Database connections (with pool status)
- Redis cache
- External services (Cloudinary, Sentry)
- Image processing capabilities
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def database_health_check() -> Dict[str, Any]:
    """Check database connection and pool health"""
    try:
        from database import SessionLocal, engine
        from sqlalchemy import text
        import sqlalchemy.pool as pool
        
        start_time = time.time()
        
        # Test basic connection
        db = SessionLocal()
        try:
            # Simple query to test connection
            result = db.execute(text("SELECT 1 as health_check"))
            health_result = result.fetchone()
            
            if health_result and health_result[0] == 1:
                response_time = round((time.time() - start_time) * 1000, 2)
                
                # Get pool information if available
                pool_info = {}
                if hasattr(engine.pool, 'size'):
                    pool_info = {
                        "pool_size": engine.pool.size(),
                        "checked_in": engine.pool.checkedin(),
                        "checked_out": engine.pool.checkedout(),
                        "overflow": getattr(engine.pool, '_overflow', 0),
                        "invalid": getattr(engine.pool, '_invalidated', 0)
                    }
                
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "connection_pool": pool_info,
                    "database_engine": str(engine.url).split("://")[0]
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Database query returned unexpected result",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2)
                }
                
        finally:
            db.close()
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }


async def cache_health_check() -> Dict[str, Any]:
    """Check Redis cache connection and performance"""
    try:
        import redis.asyncio as redis
        import os
        
        start_time = time.time()
        
        # Get Redis URL from environment
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # Create Redis client
        redis_client = redis.from_url(redis_url)
        
        try:
            # Test basic operations
            test_key = "health_check_key"
            test_value = f"health_check_{int(time.time())}"
            
            # Set a test value
            await redis_client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
            
            # Get the test value back
            retrieved_value = await redis_client.get(test_key)
            
            if retrieved_value and retrieved_value.decode() == test_value:
                # Clean up test key
                await redis_client.delete(test_key)
                
                # Get Redis info
                info = await redis_client.info()
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "redis_version": info.get("redis_version", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Redis set/get operation failed",
                    "response_time_ms": round((time.time() - start_time) * 1000, 2)
                }
                
        finally:
            await redis_client.close()
            
    except ImportError:
        # Redis not available - use in-memory fallback
        return {
            "status": "fallback",
            "message": "Redis not available - using in-memory cache",
            "response_time_ms": 0.1
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }


async def cloudinary_health_check() -> Dict[str, Any]:
    """Check Cloudinary service connectivity"""
    try:
        import cloudinary.api
        import os
        
        start_time = time.time()
        
        # Check if Cloudinary credentials are configured
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            return {
                "status": "not_configured",
                "message": "Cloudinary credentials not configured",
                "response_time_ms": 0
            }
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Test API connectivity by getting account usage
        result = cloudinary.api.usage()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "cloud_name": cloud_name,
            "plan": result.get("plan", "unknown"),
            "usage": {
                "credits_used": result.get("credits", {}).get("used", 0),
                "credits_limit": result.get("credits", {}).get("limit", 0),
                "bandwidth_used": result.get("bandwidth", {}).get("used", 0)
            }
        }
        
    except ImportError:
        return {
            "status": "not_available",
            "message": "Cloudinary library not installed",
            "response_time_ms": 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }


async def sentry_health_check() -> Dict[str, Any]:
    """Check Sentry configuration and connectivity"""
    try:
        import sentry_sdk
        import os
        
        start_time = time.time()
        
        # Check if Sentry DSN is configured
        sentry_dsn = os.getenv("SENTRY_DSN")
        
        if not sentry_dsn:
            return {
                "status": "not_configured",
                "message": "Sentry DSN not configured",
                "response_time_ms": 0
            }
        
        # Check if Sentry client is initialized
        client = sentry_sdk.Hub.current.client
        
        if client is None:
            return {
                "status": "not_initialized",
                "message": "Sentry client not initialized",
                "response_time_ms": round((time.time() - start_time) * 1000, 2)
            }
        
        # Test connectivity by capturing a test message
        # (This will be filtered out in production with proper Sentry configuration)
        event_id = sentry_sdk.capture_message("Health check test", level="info")
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "dsn_configured": bool(sentry_dsn),
            "client_initialized": True,
            "test_event_id": str(event_id) if event_id else None
        }
        
    except ImportError:
        return {
            "status": "not_available",
            "message": "Sentry library not installed",
            "response_time_ms": 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }


async def image_processing_health_check() -> Dict[str, Any]:
    """Check image processing capabilities"""
    try:
        import numpy as np
        import cv2
        from PIL import Image
        import io
        
        start_time = time.time()
        
        # Test basic image operations
        # Create a small test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Test OpenCV operations
        gray = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Test PIL operations
        pil_image = Image.fromarray(test_image)
        resized = pil_image.resize((50, 50))
        
        # Test image encoding/decoding
        buffer = io.BytesIO()
        resized.save(buffer, format='JPEG')
        buffer.seek(0)
        decoded = Image.open(buffer)
        
        # Check MediaPipe availability
        mediapipe_available = False
        try:
            import mediapipe as mp
            mediapipe_available = True
        except ImportError:
            pass
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "opencv_version": cv2.__version__,
            "pillow_available": True,
            "numpy_available": True,
            "mediapipe_available": mediapipe_available,
            "test_operations_successful": True
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }


async def enhanced_skin_analyzer_health_check() -> Dict[str, Any]:
    """Check enhanced skin tone analyzer functionality"""
    try:
        from enhanced_skin_tone_analyzer import EnhancedSkinToneAnalyzer
        import numpy as np
        
        start_time = time.time()
        
        # Initialize analyzer
        analyzer = EnhancedSkinToneAnalyzer()
        
        # Create a test image (simulating skin tone)
        test_image = np.full((200, 200, 3), [220, 180, 140], dtype=np.uint8)
        
        # Test monk skin tones data
        mock_monk_tones = {
            'Monk 1': '#f6ede4',
            'Monk 5': '#d7bd96', 
            'Monk 10': '#292420'
        }
        
        # Test skin tone analysis
        result = analyzer.analyze_skin_tone(test_image, mock_monk_tones)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if result and 'success' in result:
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "analyzer_initialized": True,
                "test_analysis_successful": result['success'],
                "supports_monk_scale": True
            }
        else:
            return {
                "status": "degraded",
                "response_time_ms": response_time,
                "error": "Test analysis failed",
                "analyzer_initialized": True
            }
            
    except ImportError:
        return {
            "status": "not_available",
            "message": "Enhanced skin tone analyzer not available",
            "response_time_ms": 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }


async def performance_systems_health_check() -> Dict[str, Any]:
    """Check performance systems health"""
    try:
        start_time = time.time()
        
        # This would be called after performance systems are initialized
        # Check if performance middleware is available
        from performance import get_performance_stats
        
        # Try to get basic stats
        stats = get_performance_stats(None)  # Pass None since we're just testing availability
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "performance_monitoring": True,
            "stats_available": isinstance(stats, dict)
        }
        
    except ImportError:
        return {
            "status": "not_available",
            "message": "Performance systems not available",
            "response_time_ms": 0
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }


def register_all_health_checks(health_manager):
    """Register all health check functions with the health manager"""
    
    # Core dependencies
    health_manager.register_dependency("database", database_health_check, timeout=10)
    health_manager.register_dependency("cache", cache_health_check, timeout=5)
    
    # External services
    health_manager.register_dependency("cloudinary", cloudinary_health_check, timeout=10)
    health_manager.register_dependency("sentry", sentry_health_check, timeout=5)
    
    # Processing capabilities
    health_manager.register_dependency("image_processing", image_processing_health_check, timeout=10)
    health_manager.register_dependency("skin_analyzer", enhanced_skin_analyzer_health_check, timeout=15)
    health_manager.register_dependency("performance_systems", performance_systems_health_check, timeout=5)
    
    logger.info("All health check dependencies registered")


async def quick_health_summary() -> Dict[str, Any]:
    """Get a quick health summary of critical systems only"""
    try:
        # Quick checks for critical systems only
        db_health = await database_health_check()
        cache_health = await cache_health_check()
        image_health = await image_processing_health_check()
        
        critical_healthy = all([
            db_health["status"] in ["healthy", "degraded"],
            cache_health["status"] in ["healthy", "fallback"],
            image_health["status"] == "healthy"
        ])
        
        return {
            "status": "healthy" if critical_healthy else "unhealthy",
            "critical_systems": {
                "database": db_health["status"],
                "cache": cache_health["status"], 
                "image_processing": image_health["status"]
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "status": "unknown",
            "error": str(e),
            "timestamp": time.time()
        }
