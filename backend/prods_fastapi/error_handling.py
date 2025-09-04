"""
Comprehensive Error Handling System for AI Fashion Backend

Addresses all error handling issues:
1. Consistent error response format
2. Enhanced error logging with request context
3. Circuit breaker pattern for external services
4. Smart fallback logic with specific error types
5. Health check dependencies verification
"""
import asyncio
import json
import logging
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


# Configure structured logging
logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error categories for consistent classification"""
    VALIDATION = "validation_error"
    AUTHENTICATION = "authentication_error"
    AUTHORIZATION = "authorization_error"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RATE_LIMIT = "rate_limit_exceeded"
    EXTERNAL_SERVICE = "external_service_error"
    DATABASE = "database_error"
    CACHE = "cache_error"
    IMAGE_PROCESSING = "image_processing_error"
    TIMEOUT = "timeout_error"
    CIRCUIT_BREAKER = "circuit_breaker_open"
    SYSTEM = "system_error"
    UNKNOWN = "unknown_error"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Structured error context for logging and debugging"""
    request_id: str
    timestamp: str
    method: str
    path: str
    user_agent: Optional[str] = None
    client_ip: Optional[str] = None
    query_params: Optional[Dict] = None
    headers: Optional[Dict] = None
    body_size: Optional[int] = None
    processing_time_ms: Optional[float] = None


@dataclass
class StandardErrorResponse:
    """Standardized error response format"""
    success: bool = False
    error: str = ""
    message: str = ""
    category: str = ErrorCategory.UNKNOWN.value
    severity: str = ErrorSeverity.MEDIUM.value
    request_id: str = ""
    timestamp: str = ""
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker implementation for external services"""
    
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        recovery_timeout: int = 30
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.last_request_time = None
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.circuit_opens = 0
    
    def can_execute(self) -> bool:
        """Check if request can be executed based on circuit state"""
        now = time.time()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        elif self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and (now - self.last_failure_time) > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit breaker {self.service_name} moving to HALF_OPEN state")
                return True
            return False
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Record successful request"""
        self.total_requests += 1
        self.successful_requests += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            logger.info(f"Circuit breaker {self.service_name} recovered - moving to CLOSED state")
    
    def record_failure(self):
        """Record failed request"""
        self.total_requests += 1
        self.failed_requests += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            if self.state == CircuitBreakerState.CLOSED:
                self.circuit_opens += 1
            self.state = CircuitBreakerState.OPEN
            logger.error(
                f"Circuit breaker {self.service_name} OPENED after {self.failure_count} failures"
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "service_name": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "circuit_opens": self.circuit_opens,
            "failure_rate": round(
                (self.failed_requests / max(self.total_requests, 1)) * 100, 2
            ),
            "last_failure_time": self.last_failure_time
        }


class CircuitBreakerManager:
    """Manage multiple circuit breakers for different services"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, service_name: str, **kwargs) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(service_name, **kwargs)
        return self.breakers[service_name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        return {name: breaker.get_stats() for name, breaker in self.breakers.items()}


# Global circuit breaker manager
circuit_manager = CircuitBreakerManager()


@asynccontextmanager
async def circuit_breaker_context(service_name: str, **breaker_kwargs):
    """Context manager for circuit breaker operations"""
    breaker = circuit_manager.get_breaker(service_name, **breaker_kwargs)
    
    if not breaker.can_execute():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Circuit breaker open",
                "message": f"Service {service_name} is currently unavailable",
                "category": ErrorCategory.CIRCUIT_BREAKER.value,
                "service": service_name,
                "state": breaker.state.value
            }
        )
    
    try:
        yield breaker
        breaker.record_success()
    except Exception as e:
        breaker.record_failure()
        raise


class SmartFallbackHandler:
    """Smart fallback logic with specific error type handling"""
    
    def __init__(self):
        self.fallback_cache = {}
        self.fallback_stats = {
            "total_fallbacks": 0,
            "by_category": {},
            "by_endpoint": {}
        }
    
    def should_fallback(self, error: Exception, category: ErrorCategory) -> bool:
        """Determine if fallback should be used based on error type"""
        
        # Never fallback for validation errors - client needs to fix input
        if category == ErrorCategory.VALIDATION:
            return False
            
        # Never fallback for authentication/authorization - security issue
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return False
        
        # Always fallback for external service and timeout errors
        if category in [
            ErrorCategory.EXTERNAL_SERVICE, 
            ErrorCategory.TIMEOUT,
            ErrorCategory.CIRCUIT_BREAKER
        ]:
            return True
        
        # Conditionally fallback for database/cache based on error type
        if category in [ErrorCategory.DATABASE, ErrorCategory.CACHE]:
            # Don't fallback for connection pool exhaustion - indicates system overload
            error_str = str(error).lower()
            if any(term in error_str for term in ["pool", "connection limit", "too many"]):
                return False
            return True
        
        # Fallback for image processing errors only if they're not critical
        if category == ErrorCategory.IMAGE_PROCESSING:
            error_str = str(error).lower()
            if any(term in error_str for term in ["corrupt", "invalid format", "unsupported"]):
                return False  # Client should fix the image
            return True
        
        return True  # Default to fallback for unknown errors
    
    def get_fallback_data(self, endpoint: str, category: ErrorCategory) -> Optional[Dict]:
        """Get appropriate fallback data for endpoint and error category"""
        
        fallback_data = {
            "/analyze-skin-tone": {
                ErrorCategory.DATABASE: {
                    'monk_skin_tone': 'Monk05',
                    'monk_tone_display': 'Monk 5',
                    'monk_hex': '#d7bd96',
                    'derived_hex_code': '#d7bd96',
                    'dominant_rgb': [215, 189, 150],
                    'confidence': 0.5,
                    'success': False,
                    'fallback_reason': 'Database unavailable - using default tone'
                },
                ErrorCategory.IMAGE_PROCESSING: {
                    'monk_skin_tone': 'Monk03',
                    'monk_tone_display': 'Monk 3',
                    'monk_hex': '#f3e7db',
                    'derived_hex_code': '#f3e7db',
                    'dominant_rgb': [243, 231, 219],
                    'confidence': 0.3,
                    'success': False,
                    'fallback_reason': 'Image processing failed - using light skin default'
                }
            },
            "/api/color-recommendations": {
                ErrorCategory.DATABASE: {
                    "colors_that_suit": [
                        {"name": "Navy Blue", "hex": "#002D72"},
                        {"name": "Forest Green", "hex": "#205C40"},
                        {"name": "Burgundy", "hex": "#890C58"},
                        {"name": "Charcoal", "hex": "#36454F"}
                    ],
                    "seasonal_type": "Universal",
                    "message": "Fallback colors - database unavailable"
                }
            },
            "/health": {
                ErrorCategory.DATABASE: {
                    "status": "degraded",
                    "database": {"status": "unhealthy", "fallback": "using_cache"},
                    "cache": {"status": "healthy"},
                    "message": "Database unavailable but cache is functioning"
                }
            }
        }
        
        endpoint_fallbacks = fallback_data.get(endpoint, {})
        return endpoint_fallbacks.get(category)
    
    def record_fallback(self, endpoint: str, category: ErrorCategory):
        """Record fallback usage for statistics"""
        self.fallback_stats["total_fallbacks"] += 1
        
        cat_name = category.value
        if cat_name not in self.fallback_stats["by_category"]:
            self.fallback_stats["by_category"][cat_name] = 0
        self.fallback_stats["by_category"][cat_name] += 1
        
        if endpoint not in self.fallback_stats["by_endpoint"]:
            self.fallback_stats["by_endpoint"][endpoint] = 0
        self.fallback_stats["by_endpoint"][endpoint] += 1


# Global fallback handler
fallback_handler = SmartFallbackHandler()


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced error logging middleware with request context"""
    
    def __init__(self, app):
        super().__init__(app)
        self.error_stats = {
            "total_errors": 0,
            "by_category": {},
            "by_endpoint": {},
            "by_status_code": {}
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle request with enhanced error logging"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Create error context
        context = ErrorContext(
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat(),
            method=request.method,
            path=request.url.path,
            user_agent=request.headers.get("user-agent"),
            client_ip=self._get_client_ip(request),
            query_params=dict(request.query_params),
            headers={k: v for k, v in request.headers.items() 
                    if k.lower() not in ["authorization", "cookie", "x-api-key"]},
            body_size=request.headers.get("content-length")
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        request.state.start_time = start_time
        
        try:
            response = await call_next(request)
            context.processing_time_ms = (time.time() - start_time) * 1000
            
            # Log successful requests with long processing times
            if context.processing_time_ms > 5000:  # 5 seconds
                logger.warning(
                    "Slow request completed",
                    extra={
                        "request_context": context.__dict__,
                        "status_code": response.status_code,
                        "response_size": response.headers.get("content-length")
                    }
                )
            
            return response
            
        except Exception as e:
            context.processing_time_ms = (time.time() - start_time) * 1000
            
            # Determine error category and severity
            category, severity = self._classify_error(e)
            
            # Create standardized error response
            error_response = self._create_error_response(e, context, category, severity)
            
            # Log error with full context
            self._log_error_with_context(e, context, category, severity)
            
            # Update error statistics
            self._update_error_stats(context.path, category, error_response.get("status_code", 500))
            
            # Check if fallback should be used
            if fallback_handler.should_fallback(e, category):
                fallback_data = fallback_handler.get_fallback_data(context.path, category)
                if fallback_data:
                    fallback_handler.record_fallback(context.path, category)
                    logger.info(f"Using fallback data for {context.path} due to {category.value}")
                    
                    # Merge fallback data with error response
                    error_response.update(fallback_data)
                    
                    return JSONResponse(
                        content=error_response,
                        status_code=200,  # Return 200 with fallback data
                        headers={"X-Fallback-Used": "true", "X-Request-ID": request_id}
                    )
            
            # Return standard error response
            status_code = self._get_status_code_for_category(category)
            if isinstance(e, (HTTPException, StarletteHTTPException)):
                status_code = e.status_code
            
            return JSONResponse(
                content=error_response,
                status_code=status_code,
                headers={"X-Request-ID": request_id}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request"""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _classify_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by category and severity"""
        error_str = str(error).lower()
        
        # HTTPException classification
        if isinstance(error, (HTTPException, StarletteHTTPException)):
            status_code = error.status_code
            if status_code == 400:
                return ErrorCategory.VALIDATION, ErrorSeverity.LOW
            elif status_code == 401:
                return ErrorCategory.AUTHENTICATION, ErrorSeverity.MEDIUM
            elif status_code == 403:
                return ErrorCategory.AUTHORIZATION, ErrorSeverity.MEDIUM
            elif status_code == 404:
                return ErrorCategory.RESOURCE_NOT_FOUND, ErrorSeverity.LOW
            elif status_code == 408:
                return ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM
            elif status_code == 413:
                return ErrorCategory.VALIDATION, ErrorSeverity.LOW
            elif status_code == 429:
                return ErrorCategory.RATE_LIMIT, ErrorSeverity.LOW
            elif status_code >= 500:
                return ErrorCategory.SYSTEM, ErrorSeverity.HIGH
        
        # Database errors
        if any(term in error_str for term in ["database", "connection", "sql", "postgresql"]):
            return ErrorCategory.DATABASE, ErrorSeverity.HIGH
        
        # Cache errors
        if any(term in error_str for term in ["redis", "cache", "memcache"]):
            return ErrorCategory.CACHE, ErrorSeverity.MEDIUM
        
        # Image processing errors
        if any(term in error_str for term in ["image", "pil", "opencv", "mediapipe"]):
            return ErrorCategory.IMAGE_PROCESSING, ErrorSeverity.MEDIUM
        
        # External service errors
        if any(term in error_str for term in ["cloudinary", "sentry", "api", "http"]):
            return ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.MEDIUM
        
        # Timeout errors
        if any(term in error_str for term in ["timeout", "asyncio.timeout"]):
            return ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM
        
        # Circuit breaker errors
        if "circuit breaker" in error_str:
            return ErrorCategory.CIRCUIT_BREAKER, ErrorSeverity.MEDIUM
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def _create_error_response(
        self, 
        error: Exception, 
        context: ErrorContext, 
        category: ErrorCategory, 
        severity: ErrorSeverity
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        
        # Base error response
        response = {
            "success": False,
            "error": type(error).__name__,
            "message": str(error),
            "category": category.value,
            "severity": severity.value,
            "request_id": context.request_id,
            "timestamp": context.timestamp,
        }
        
        # Add suggestions based on error category
        suggestions = self._get_error_suggestions(category, error)
        if suggestions:
            response["suggestions"] = suggestions
        
        # Add details for certain error types
        if category in [ErrorCategory.VALIDATION, ErrorCategory.RATE_LIMIT]:
            response["details"] = self._get_error_details(error, category)
        
        return response
    
    def _get_error_suggestions(self, category: ErrorCategory, error: Exception) -> List[str]:
        """Get helpful suggestions based on error category"""
        suggestions_map = {
            ErrorCategory.VALIDATION: [
                "Check your request parameters and format",
                "Ensure required fields are provided",
                "Verify file types and sizes meet requirements"
            ],
            ErrorCategory.AUTHENTICATION: [
                "Verify your API key or authentication credentials",
                "Check if your session has expired"
            ],
            ErrorCategory.RATE_LIMIT: [
                "Reduce your request frequency",
                "Implement exponential backoff",
                "Consider upgrading your rate limit plan"
            ],
            ErrorCategory.TIMEOUT: [
                "Try reducing image size for faster processing",
                "Check your network connection",
                "Retry the request after a short delay"
            ],
            ErrorCategory.EXTERNAL_SERVICE: [
                "The issue may be temporary - try again later",
                "Check service status pages for known issues"
            ],
            ErrorCategory.DATABASE: [
                "The issue may be temporary - try again later",
                "Contact support if the problem persists"
            ],
            ErrorCategory.IMAGE_PROCESSING: [
                "Ensure your image is in a supported format (JPEG, PNG)",
                "Try reducing image size if it's very large",
                "Check that the image is not corrupted"
            ]
        }
        return suggestions_map.get(category, ["Try again later or contact support"])
    
    def _get_error_details(self, error: Exception, category: ErrorCategory) -> Dict[str, Any]:
        """Get additional error details"""
        details = {}
        
        if isinstance(error, (HTTPException, StarletteHTTPException)):
            if hasattr(error, 'detail') and isinstance(error.detail, dict):
                details.update(error.detail)
        
        return details
    
    def _get_status_code_for_category(self, category: ErrorCategory) -> int:
        """Get appropriate HTTP status code for error category"""
        status_map = {
            ErrorCategory.VALIDATION: 400,
            ErrorCategory.AUTHENTICATION: 401,
            ErrorCategory.AUTHORIZATION: 403,
            ErrorCategory.RESOURCE_NOT_FOUND: 404,
            ErrorCategory.TIMEOUT: 408,
            ErrorCategory.RATE_LIMIT: 429,
            ErrorCategory.EXTERNAL_SERVICE: 502,
            ErrorCategory.CIRCUIT_BREAKER: 503,
            ErrorCategory.DATABASE: 503,
            ErrorCategory.CACHE: 503,
            ErrorCategory.IMAGE_PROCESSING: 422,
            ErrorCategory.SYSTEM: 500,
            ErrorCategory.UNKNOWN: 500
        }
        return status_map.get(category, 500)
    
    def _log_error_with_context(
        self, 
        error: Exception, 
        context: ErrorContext, 
        category: ErrorCategory, 
        severity: ErrorSeverity
    ):
        """Log error with full context"""
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_category": category.value,
            "error_severity": severity.value,
            "request_context": context.__dict__,
            "stack_trace": traceback.format_exc() if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
        }
        
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[severity]
        
        logger.log(
            log_level,
            f"Request failed: {context.method} {context.path}",
            extra=log_data
        )
    
    def _update_error_stats(self, path: str, category: ErrorCategory, status_code: int):
        """Update error statistics"""
        self.error_stats["total_errors"] += 1
        
        # By category
        cat_name = category.value
        if cat_name not in self.error_stats["by_category"]:
            self.error_stats["by_category"][cat_name] = 0
        self.error_stats["by_category"][cat_name] += 1
        
        # By endpoint
        if path not in self.error_stats["by_endpoint"]:
            self.error_stats["by_endpoint"][path] = 0
        self.error_stats["by_endpoint"][path] += 1
        
        # By status code
        if status_code not in self.error_stats["by_status_code"]:
            self.error_stats["by_status_code"][status_code] = 0
        self.error_stats["by_status_code"][status_code] += 1
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return self.error_stats.copy()


class HealthCheckDependencies:
    """Enhanced health check with dependency verification"""
    
    def __init__(self):
        self.dependencies = {}
        self.health_cache = {}
        self.cache_ttl = 30  # 30 seconds cache
    
    def register_dependency(self, name: str, check_func: Callable, timeout: int = 5):
        """Register a dependency health check"""
        self.dependencies[name] = {
            "check_func": check_func,
            "timeout": timeout,
            "last_check": None,
            "last_status": None,
            "consecutive_failures": 0
        }
    
    async def check_dependency_health(self, name: str) -> Dict[str, Any]:
        """Check health of a specific dependency"""
        if name not in self.dependencies:
            return {"status": "unknown", "error": f"Dependency {name} not registered"}
        
        dep = self.dependencies[name]
        now = time.time()
        
        # Use cached result if recent
        if (dep["last_check"] and 
            now - dep["last_check"] < self.cache_ttl and 
            dep["last_status"] is not None):
            return dep["last_status"]
        
        try:
            # Run health check with timeout
            result = await asyncio.wait_for(
                dep["check_func"](),
                timeout=dep["timeout"]
            )
            
            # Success
            dep["consecutive_failures"] = 0
            dep["last_check"] = now
            dep["last_status"] = {
                "status": "healthy",
                "response_time_ms": round((time.time() - now) * 1000, 2),
                **(result if isinstance(result, dict) else {"details": str(result)})
            }
            
        except asyncio.TimeoutError:
            dep["consecutive_failures"] += 1
            dep["last_check"] = now
            dep["last_status"] = {
                "status": "unhealthy",
                "error": f"Health check timeout after {dep['timeout']}s",
                "consecutive_failures": dep["consecutive_failures"]
            }
            
        except Exception as e:
            dep["consecutive_failures"] += 1
            dep["last_check"] = now
            dep["last_status"] = {
                "status": "unhealthy",
                "error": str(e),
                "consecutive_failures": dep["consecutive_failures"]
            }
        
        return dep["last_status"]
    
    async def check_all_dependencies(self) -> Dict[str, Any]:
        """Check health of all dependencies"""
        results = {}
        overall_healthy = True
        
        for name in self.dependencies.keys():
            result = await self.check_dependency_health(name)
            results[name] = result
            if result["status"] != "healthy":
                overall_healthy = False
        
        return {
            "overall_status": "healthy" if overall_healthy else "degraded",
            "dependencies": results,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global health check manager
health_manager = HealthCheckDependencies()


def setup_error_handling(app):
    """Setup comprehensive error handling for FastAPI app"""
    
    # Add error logging middleware
    error_middleware = ErrorLoggingMiddleware(app)
    app.add_middleware(ErrorLoggingMiddleware)
    
    # Store middleware reference for stats access
    app.state.error_middleware = error_middleware
    app.state.circuit_manager = circuit_manager
    app.state.fallback_handler = fallback_handler
    app.state.health_manager = health_manager
    
    logger.info("Comprehensive error handling system initialized")
    
    return app


# Utility functions for use in endpoints
def get_error_stats(app) -> Dict[str, Any]:
    """Get comprehensive error statistics"""
    stats = {}
    
    if hasattr(app.state, 'error_middleware'):
        stats["errors"] = app.state.error_middleware.get_error_stats()
    
    if hasattr(app.state, 'circuit_manager'):
        stats["circuit_breakers"] = app.state.circuit_manager.get_all_stats()
    
    if hasattr(app.state, 'fallback_handler'):
        stats["fallbacks"] = app.state.fallback_handler.fallback_stats
    
    return stats


async def enhanced_health_check(app) -> Dict[str, Any]:
    """Enhanced health check with all dependencies"""
    if hasattr(app.state, 'health_manager'):
        return await app.state.health_manager.check_all_dependencies()
    
    return {"status": "unknown", "message": "Health manager not initialized"}
