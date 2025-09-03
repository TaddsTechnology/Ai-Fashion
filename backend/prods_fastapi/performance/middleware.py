"""
Performance Middleware for Request Timeouts and Response Compression
"""
import asyncio
import gzip
import time
import logging
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from starlette.middleware.gzip import GZipMiddleware
import json

logger = logging.getLogger(__name__)

class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to handle request timeouts"""
    
    def __init__(self, app, timeout_seconds: int = 30):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
        self.long_timeout_paths = {
            '/analyze-skin-tone': 60,  # Image analysis needs more time
            '/api/color-recommendations': 45,  # Database queries can be slower
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle request with timeout"""
        start_time = time.time()
        
        # Determine timeout based on path
        path = request.url.path
        timeout = self.long_timeout_paths.get(path, self.timeout_seconds)
        
        try:
            # Create timeout task
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout
            )
            
            # Log slow requests
            elapsed = time.time() - start_time
            if elapsed > (timeout * 0.8):  # Log if using 80%+ of timeout
                logger.warning(
                    f"Slow request: {request.method} {path} took {elapsed:.2f}s "
                    f"(timeout: {timeout}s)"
                )
            
            return response
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            logger.error(
                f"Request timeout: {request.method} {path} took {elapsed:.2f}s "
                f"(timeout: {timeout}s)"
            )
            
            return Response(
                content=json.dumps({
                    "error": "Request timeout",
                    "message": f"Request took longer than {timeout} seconds",
                    "elapsed_seconds": round(elapsed, 2)
                }),
                status_code=408,
                media_type="application/json"
            )
        
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Request error: {request.method} {path} failed after {elapsed:.2f}s: {e}"
            )
            raise

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor request performance"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_stats = {
            'total_requests': 0,
            'total_time_ms': 0.0,
            'avg_time_ms': 0.0,
            'slow_requests': 0,
            'errors': 0,
            'path_stats': {}
        }
        self.slow_request_threshold = 1.0  # 1 second
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance"""
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        try:
            response = await call_next(request)
            
            # Calculate timing
            elapsed = time.time() - start_time
            elapsed_ms = elapsed * 1000
            
            # Update stats
            self._update_stats(path, method, elapsed_ms, response.status_code)
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"
            response.headers["X-Request-ID"] = str(id(request))
            
            # Log slow requests
            if elapsed > self.slow_request_threshold:
                logger.info(
                    f"Slow request: {method} {path} - {elapsed_ms:.2f}ms "
                    f"(status: {response.status_code})"
                )
            
            return response
            
        except Exception as e:
            elapsed = time.time() - start_time
            elapsed_ms = elapsed * 1000
            
            # Update error stats
            self._update_stats(path, method, elapsed_ms, 500, error=True)
            
            logger.error(f"Request failed: {method} {path} - {elapsed_ms:.2f}ms - {e}")
            raise
    
    def _update_stats(self, path: str, method: str, elapsed_ms: float, status_code: int, error: bool = False):
        """Update performance statistics"""
        key = f"{method} {path}"
        
        # Update global stats
        self.request_stats['total_requests'] += 1
        self.request_stats['total_time_ms'] += elapsed_ms
        self.request_stats['avg_time_ms'] = (
            self.request_stats['total_time_ms'] / self.request_stats['total_requests']
        )
        
        if elapsed_ms > (self.slow_request_threshold * 1000):
            self.request_stats['slow_requests'] += 1
            
        if error or status_code >= 400:
            self.request_stats['errors'] += 1
        
        # Update path-specific stats
        if key not in self.request_stats['path_stats']:
            self.request_stats['path_stats'][key] = {
                'count': 0,
                'total_time_ms': 0.0,
                'avg_time_ms': 0.0,
                'min_time_ms': float('inf'),
                'max_time_ms': 0.0,
                'errors': 0
            }
        
        path_stat = self.request_stats['path_stats'][key]
        path_stat['count'] += 1
        path_stat['total_time_ms'] += elapsed_ms
        path_stat['avg_time_ms'] = path_stat['total_time_ms'] / path_stat['count']
        path_stat['min_time_ms'] = min(path_stat['min_time_ms'], elapsed_ms)
        path_stat['max_time_ms'] = max(path_stat['max_time_ms'], elapsed_ms)
        
        if error or status_code >= 400:
            path_stat['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = self.request_stats.copy()
        
        # Calculate additional metrics
        total_requests = stats['total_requests']
        if total_requests > 0:
            stats['error_rate_percent'] = round(
                (stats['errors'] / total_requests) * 100, 2
            )
            stats['slow_request_rate_percent'] = round(
                (stats['slow_requests'] / total_requests) * 100, 2
            )
        else:
            stats['error_rate_percent'] = 0.0
            stats['slow_request_rate_percent'] = 0.0
        
        # Clean up path stats for infinite min times
        for path_key, path_stat in stats['path_stats'].items():
            if path_stat['min_time_ms'] == float('inf'):
                path_stat['min_time_ms'] = 0.0
        
        return stats

class SmartCompressionMiddleware(BaseHTTPMiddleware):
    """Smart compression middleware that selectively compresses responses"""
    
    def __init__(self, app, minimum_size: int = 1000, compression_level: int = 6):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        
        # Content types that should be compressed
        self.compressible_types = {
            'application/json',
            'application/javascript',
            'text/html',
            'text/css',
            'text/plain',
            'text/xml',
            'application/xml',
            'application/x-javascript'
        }
        
        # Content types that should NOT be compressed (already compressed or binary)
        self.non_compressible_types = {
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
            'audio/mpeg',
            'video/mp4',
            'application/gzip',
            'application/zip'
        }
        
    async def dispatch(self, request: Request, call_next: Callable) -> StarletteResponse:
        """Apply smart compression based on content type and size"""
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get('accept-encoding', '')
        if 'gzip' not in accept_encoding.lower():
            return await call_next(request)
        
        response = await call_next(request)
        
        # Check if already compressed
        if response.headers.get('content-encoding'):
            return response
            
        # Get content type
        content_type = response.headers.get('content-type', '').split(';')[0].lower()
        
        # Skip non-compressible content
        if content_type in self.non_compressible_types:
            return response
        
        # Only compress if content type is compressible or unknown large content
        if content_type not in self.compressible_types and content_type:
            return response
        
        # Get response body
        if hasattr(response, 'body'):
            body = response.body
        else:
            # For streaming responses, we can't easily compress
            return response
        
        # Check minimum size
        if len(body) < self.minimum_size:
            return response
        
        try:
            # Compress the body
            compressed_body = gzip.compress(body, compresslevel=self.compression_level)
            
            # Check if compression is beneficial (at least 10% reduction)
            if len(compressed_body) >= len(body) * 0.9:
                return response
            
            # Create new response with compressed body
            response.headers['content-encoding'] = 'gzip'
            response.headers['content-length'] = str(len(compressed_body))
            response.headers['vary'] = 'Accept-Encoding'
            
            # Create new response object
            compressed_response = StarletteResponse(
                content=compressed_body,
                status_code=response.status_code,
                headers=response.headers,
                media_type=response.media_type
            )
            
            # Log compression stats
            compression_ratio = len(body) / len(compressed_body)
            logger.debug(
                f"Compressed response: {len(body)} -> {len(compressed_body)} bytes "
                f"(ratio: {compression_ratio:.2f}x, saved: {len(body) - len(compressed_body)} bytes)"
            )
            
            return compressed_response
            
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return response

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size"""
    
    def __init__(self, app, max_size_mb: int = 10):
        super().__init__(app)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Different limits for different endpoints
        self.endpoint_limits = {
            '/analyze-skin-tone': 5 * 1024 * 1024,  # 5MB for images
            '/api/color-recommendations': 1024,  # 1KB for API requests
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check request size before processing"""
        
        # Get content length
        content_length = request.headers.get('content-length')
        if not content_length:
            return await call_next(request)
        
        try:
            content_length = int(content_length)
        except ValueError:
            return await call_next(request)
        
        # Determine size limit for this endpoint
        path = request.url.path
        size_limit = self.endpoint_limits.get(path, self.max_size_bytes)
        
        if content_length > size_limit:
            logger.warning(
                f"Request too large: {path} - {content_length} bytes "
                f"(limit: {size_limit} bytes)"
            )
            
            return Response(
                content=json.dumps({
                    "error": "Request too large",
                    "message": f"Request body must be smaller than {size_limit // (1024*1024)}MB",
                    "received_size_bytes": content_length,
                    "limit_size_bytes": size_limit
                }),
                status_code=413,
                media_type="application/json"
            )
        
        return await call_next(request)

def add_performance_middleware(app):
    """Add all performance middleware to the FastAPI app"""
    
    # Add middleware in reverse order (they wrap around each other)
    
    # 1. Request size limiting (outermost)
    app.add_middleware(RequestSizeLimitMiddleware, max_size_mb=10)
    
    # 2. Compression
    app.add_middleware(SmartCompressionMiddleware, minimum_size=1000, compression_level=6)
    
    # 3. Performance monitoring
    performance_middleware = PerformanceMonitoringMiddleware(app)
    app.add_middleware(PerformanceMonitoringMiddleware)
    
    # 4. Request timeout (innermost - closest to the actual request handling)
    app.add_middleware(RequestTimeoutMiddleware, timeout_seconds=30)
    
    # Store reference to performance middleware for stats access
    app.state.performance_middleware = performance_middleware
    
    logger.info("Performance middleware added to FastAPI app")
    
    return app
