"""
Sentry Integration for AI Fashion Backend
Comprehensive monitoring, error tracking, and performance analysis
"""

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Optional integrations - import only if available
try:
    from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    from sentry_sdk.integrations.redis import RedisIntegration
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
    ASYNCIO_AVAILABLE = True
except ImportError:
    ASYNCIO_AVAILABLE = False

import logging
from typing import Dict, Any, Optional
from functools import wraps
import time
import asyncio

try:
    from config import settings
except ImportError:
    # Fallback configuration if config module fails
    import os
    class FallbackSettings:
        sentry_dsn = os.getenv("SENTRY_DSN", "")
        sentry_environment = os.getenv("SENTRY_ENVIRONMENT", "production")
        sentry_traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
        app_version = os.getenv("APP_VERSION", "1.0.0")
    settings = FallbackSettings()

logger = logging.getLogger(__name__)

class EnhancedSentryService:
    """Enhanced Sentry service for comprehensive AI Fashion monitoring"""
    
    @classmethod
    def initialize(cls):
        """Initialize Sentry with comprehensive integrations"""
        if not settings.sentry_dsn:
            logger.warning("Sentry DSN not configured, skipping initialization")
            return
        
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        
        # Build integrations list
        integrations = [logging_integration, FastApiIntegration()]
        
        if SQLALCHEMY_AVAILABLE:
            integrations.append(SqlAlchemyIntegration())
        
        if REDIS_AVAILABLE:
            integrations.append(RedisIntegration())
        
        if ASYNCIO_AVAILABLE:
            integrations.append(AsyncioIntegration())
        
        # Initialize Sentry with all integrations
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            
            # Performance Monitoring
            traces_sample_rate=getattr(settings, 'sentry_traces_sample_rate', 0.1),
            profiles_sample_rate=0.1,
            
            # Environment and Release Tracking
            environment=getattr(settings, 'sentry_environment', 'production'),
            release=f"ai-fashion@{getattr(settings, 'app_version', '1.0.0')}",
            
            # Integrations
            integrations=integrations,
            
            # Data Collection
            send_default_pii=False,  # Don't send personal data
            attach_stacktrace=True,
            
            # Custom Tags
            before_send=cls._before_send_filter,
        )
        
        # Set global tags
        sentry_sdk.set_tag("component", "ai-fashion-backend")
        sentry_sdk.set_tag("service", "skin-tone-analysis")
        
        logger.info(f"Sentry initialized for environment: {getattr(settings, 'sentry_environment', 'production')}")
    
    @staticmethod
    def _before_send_filter(event, hint):
        """Filter and enhance events before sending to Sentry"""
        # Add custom context
        if 'request' in event:
            event['tags'] = event.get('tags', {})
            event['tags']['api_version'] = getattr(settings, 'app_version', '1.0.0')
        
        # Filter out common non-critical errors
        exception = hint.get('exc_info')
        if exception:
            exc_type, exc_value, tb = exception
            # Skip client disconnection errors
            if 'ConnectionResetError' in str(exc_type):
                return None
        
        return event
    
    @staticmethod
    def get_middleware(app):
        """Wrap ASGI app with Sentry middleware"""
        return SentryAsgiMiddleware(app)
    
    @staticmethod
    def capture_skin_tone_analysis(user_id: str, image_data: Dict, result: Dict):
        """Capture skin tone analysis event with context"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("analysis_type", "skin_tone")
            scope.set_tag("monk_tone", result.get('monk_skin_tone', 'unknown'))
            scope.set_context("analysis_result", {
                "confidence": result.get('confidence', 0),
                "method": result.get('analysis_method', 'unknown'),
                "success": result.get('success', False),
                "processing_time": result.get('processing_time', 0)
            })
            scope.set_context("image_info", {
                "size": image_data.get('size', 0),
                "format": image_data.get('format', 'unknown'),
                "dimensions": image_data.get('dimensions', 'unknown')
            })
            scope.set_user({"id": user_id})
            
            # Capture as breadcrumb for successful analysis
            if result.get('success'):
                sentry_sdk.add_breadcrumb(
                    message="Skin tone analysis completed",
                    category="analysis",
                    level="info",
                    data={
                        "monk_tone": result.get('monk_skin_tone'),
                        "confidence": result.get('confidence')
                    }
                )
    
    @staticmethod
    def capture_cloudinary_upload(public_id: str, upload_result: Dict):
        """Capture Cloudinary upload events"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("service", "cloudinary")
            scope.set_context("upload_result", {
                "public_id": public_id,
                "success": upload_result.get('success', False),
                "url": upload_result.get('url', ''),
                "size": upload_result.get('bytes', 0)
            })
            
            if upload_result.get('success'):
                sentry_sdk.add_breadcrumb(
                    message="Image uploaded to Cloudinary",
                    category="upload",
                    level="info",
                    data={"public_id": public_id}
                )
            else:
                sentry_sdk.capture_message(
                    "Cloudinary upload failed",
                    level="error"
                )
    
    @staticmethod
    def capture_model_performance(model_name: str, metrics: Dict):
        """Capture ML model performance metrics"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("model", model_name)
            scope.set_context("model_metrics", metrics)
            
            sentry_sdk.add_breadcrumb(
                message=f"Model {model_name} performance recorded",
                category="ml_performance",
                level="info",
                data=metrics
            )
    
    @staticmethod
    def monitor_api_endpoint(endpoint_name: str):
        """Decorator to monitor API endpoint performance"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                with sentry_sdk.configure_scope() as scope:
                    scope.set_tag("endpoint", endpoint_name)
                    
                try:
                    result = await func(*args, **kwargs)
                    processing_time = time.time() - start_time
                    
                    # Record successful execution
                    sentry_sdk.add_breadcrumb(
                        message=f"API endpoint {endpoint_name} completed",
                        category="api",
                        level="info",
                        data={
                            "processing_time": processing_time,
                            "success": True
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    
                    # Capture error with context
                    with sentry_sdk.configure_scope() as scope:
                        scope.set_context("error_context", {
                            "endpoint": endpoint_name,
                            "processing_time": processing_time,
                            "args_count": len(args),
                            "kwargs_keys": list(kwargs.keys())
                        })
                        
                    sentry_sdk.capture_exception(e)
                    raise
                    
            return wrapper
        return decorator
    
    @staticmethod
    def track_user_journey(user_id: str, action: str, metadata: Optional[Dict] = None):
        """Track user journey through the app"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_user({"id": user_id})
            scope.set_tag("user_action", action)
            
            sentry_sdk.add_breadcrumb(
                message=f"User action: {action}",
                category="user_journey",
                level="info",
                data=metadata or {}
            )
    
    @staticmethod
    def capture_business_metric(metric_name: str, value: float, tags: Optional[Dict] = None):
        """Capture custom business metrics"""
        with sentry_sdk.configure_scope() as scope:
            if tags:
                for key, val in tags.items():
                    scope.set_tag(key, val)
            
            scope.set_context("business_metric", {
                "name": metric_name,
                "value": value
            })
            
            sentry_sdk.add_breadcrumb(
                message=f"Business metric recorded: {metric_name}",
                category="business",
                level="info",
                data={"metric": metric_name, "value": value}
            )

# Legacy class for backward compatibility
class SentryService(EnhancedSentryService):
    pass

# Initialize Sentry on import
EnhancedSentryService.initialize()
