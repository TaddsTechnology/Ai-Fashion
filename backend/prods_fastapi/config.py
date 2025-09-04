"""
Configuration Settings for AI Fashion Backend Performance Optimization
"""

import os
from typing import Dict, Any, List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "AI Fashion Backend"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ai_fashion_dev")
    async_database_url: str = ""  # Will be derived from database_url
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    db_echo: bool = False
    
    # Redis/Cache settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_max_connections: int = 10
    cache_default_ttl: int = 3600
    
    # Background task settings
    dramatiq_broker_url: str = os.getenv("DRAMATIQ_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/1"))
    max_background_tasks: int = 10
    task_timeout: int = 300
    
    # Performance settings
    max_workers: int = 4
    worker_connections: int = 1000
    keepalive_timeout: int = 5
    request_timeout: int = 30
    
    # Monitoring settings
    enable_metrics: bool = True
    metrics_path: str = "/metrics"
    health_check_path: str = "/health"
    enable_request_logging: bool = True
    
    # Image processing settings
    max_image_size_mb: int = 10
    max_image_width: int = 2000
    max_image_height: int = 2000
    image_processing_timeout: int = 30
    
    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200
    
    # Security settings
    cors_origins: str = "https://*.render.com,http://localhost:3000,http://localhost:5173,*"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    cors_allow_headers: str = "*"
    
    # CDN settings
    cdn_enabled: bool = False
    cdn_base_url: str = ""
    s3_bucket_name: str = ""
    s3_region: str = "us-east-1"
    
    # Cloudinary settings
    cloudinary_cloud_name: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY", "")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    # Sentry settings
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    sentry_environment: str = os.getenv("SENTRY_ENVIRONMENT", "production")
    sentry_traces_sample_rate: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    
    # Load balancing settings
    load_balancer_enabled: bool = False
    sticky_sessions: bool = False
    health_check_interval: int = 30
    
    # Alert thresholds
    alert_cpu_threshold: float = 90.0
    alert_memory_threshold: float = 90.0
    alert_disk_threshold: float = 85.0
    alert_error_rate_threshold: float = 15.0
    alert_response_time_threshold: float = 3.0
    
    # Caching strategies
    cache_skin_tone_ttl: int = 7200  # 2 hours
    cache_color_analysis_ttl: int = 3600  # 1 hour
    cache_recommendations_ttl: int = 1800  # 30 minutes
    cache_image_processing_ttl: int = 7200  # 2 hours
    
    # Background task intervals
    cache_warmup_interval: int = 3600  # 1 hour
    cache_cleanup_interval: int = 3600  # 1 hour
    health_check_interval_bg: int = 60  # 1 minute
    metrics_cleanup_interval: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Derive async database URL if not provided
        if not self.async_database_url:
            self.async_database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )

# Global settings instance
settings = Settings()

# Performance optimization configurations
PERFORMANCE_CONFIG = {
    "image_processing": {
        "enable_gpu": False,  # Set to True if CUDA is available
        "max_concurrent_processes": settings.max_workers,
        "resize_before_processing": True,
        "use_background_tasks": True,
        "cache_processed_images": True
    },
    
    "database": {
        "use_connection_pooling": True,
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "enable_query_caching": True,
        "use_async_operations": True,
        "batch_operations": True
    },
    
    "caching": {
        "enabled": True,
        "backend": "redis",
        "compression": True,
        "serialization": "pickle",
        "key_prefix": "ai_fashion:",
        "cluster_mode": False
    },
    
    "load_balancing": {
        "algorithm": "round_robin",  # round_robin, least_connections, ip_hash
        "health_checks": True,
        "sticky_sessions": settings.sticky_sessions,
        "session_affinity": "none"
    },
    
    "cdn": {
        "provider": "cloudflare",  # cloudflare, aws_cloudfront, azure_cdn
        "cache_control": "public, max-age=31536000",  # 1 year for static assets
        "compress_images": True,
        "webp_support": True
    }
}

# Microservice configuration
MICROSERVICE_CONFIG = {
    "image_processing_service": {
        "enabled": False,  # Set to True to enable microservice architecture
        "url": "http://localhost:8001",
        "timeout": settings.image_processing_timeout,
        "retry_attempts": 3
    },
    
    "color_analysis_service": {
        "enabled": False,
        "url": "http://localhost:8002", 
        "timeout": 10,
        "retry_attempts": 3
    },
    
    "recommendation_service": {
        "enabled": False,
        "url": "http://localhost:8003",
        "timeout": 15,
        "retry_attempts": 2
    }
}

# Monitoring configuration
MONITORING_CONFIG = {
    "prometheus": {
        "enabled": settings.enable_metrics,
        "port": 9090,
        "scrape_interval": "15s",
        "metrics_path": settings.metrics_path
    },
    
    "grafana": {
        "enabled": False,
        "port": 3000,
        "dashboard_url": "/grafana"
    },
    
    "alerts": {
        "slack_webhook": os.getenv("SLACK_WEBHOOK_URL", ""),
        "email_smtp_server": os.getenv("SMTP_SERVER", ""),
        "email_notifications": os.getenv("ALERT_EMAIL", "").split(",") if os.getenv("ALERT_EMAIL") else []
    }
}

# Feature flags
FEATURE_FLAGS = {
    "enable_ab_testing": True,
    "enable_advanced_recommendations": True,
    "enable_background_processing": True,
    "enable_caching": True,
    "enable_rate_limiting": settings.enable_rate_limiting,
    "enable_metrics": settings.enable_metrics,
    "enable_health_checks": True,
    "enable_request_logging": settings.enable_request_logging,
    "enable_compression": True,
    "enable_async_db": True
}

def get_worker_config() -> Dict[str, Any]:
    """Get Uvicorn worker configuration"""
    return {
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8000)),
        "workers": settings.max_workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "worker_connections": settings.worker_connections,
        "keepalive": settings.keepalive_timeout,
        "timeout": settings.request_timeout,
        "max_requests": 1000,
        "max_requests_jitter": 100,
        "preload_app": True,
        "access_log": settings.enable_request_logging,
        "log_level": "info" if not settings.debug else "debug"
    }

def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration"""
    return {
        "url": settings.redis_url,
        "max_connections": settings.redis_max_connections,
        "decode_responses": False,
        "socket_timeout": 5,
        "socket_connect_timeout": 5,
        "retry_on_timeout": True,
        "health_check_interval": 30
    }

def get_database_config() -> Dict[str, Any]:
    """Get database configuration"""
    return {
        "url": settings.database_url,
        "async_url": settings.async_database_url,
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_timeout": settings.db_pool_timeout,
        "pool_recycle": settings.db_pool_recycle,
        "echo": settings.db_echo,
        "future": True,
        "pool_pre_ping": True
    }

# Environment-specific configurations
def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return {
            "debug": False,
            "workers": max(2, settings.max_workers),
            "log_level": "warning",
            "enable_metrics": True,
            "enable_health_checks": True,
            "cache_ttl_multiplier": 2.0,
            "rate_limit_strict": True
        }
    elif env == "staging":
        return {
            "debug": False,
            "workers": max(1, settings.max_workers // 2),
            "log_level": "info",
            "enable_metrics": True,
            "enable_health_checks": True,
            "cache_ttl_multiplier": 1.5,
            "rate_limit_strict": False
        }
    else:  # development
        return {
            "debug": True,
            "workers": 1,
            "log_level": "debug",
            "enable_metrics": False,
            "enable_health_checks": True,
            "cache_ttl_multiplier": 0.5,
            "rate_limit_strict": False
        }

# Validate configuration on import
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check required environment variables
    required_env_vars = ["DATABASE_URL"]
    for var in required_env_vars:
        if not os.getenv(var) and not getattr(settings, var.lower(), None):
            errors.append(f"Missing required environment variable: {var}")
    
    # Validate numeric ranges
    if settings.db_pool_size < 1:
        errors.append("Database pool size must be at least 1")
    
    if settings.max_workers < 1:
        errors.append("Max workers must be at least 1")
    
    if settings.cache_default_ttl < 60:
        errors.append("Cache TTL should be at least 60 seconds")
    
    # Validate URLs
    if not settings.database_url.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite:///")):
        errors.append("Database URL must be PostgreSQL or SQLite")
    
    if not settings.redis_url.startswith(("redis://", "rediss://")):
        errors.append("Redis URL must start with redis:// or rediss://")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")

# Validate configuration on import
try:
    validate_config()
except ValueError as e:
    print(f"Configuration validation failed: {e}")
    # Continue with defaults in development
    if os.getenv("ENVIRONMENT", "development").lower() == "development":
        print("Continuing with default configuration for development...")
    else:
        raise
