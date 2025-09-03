"""
Additional API Testing and Error Monitoring Tools
Complements your existing Sentry setup
"""
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import httpx
import json

logger = logging.getLogger(__name__)

class APIHealthChecker:
    """Automated API health checking and testing"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run comprehensive API health checks"""
        results = {}
        
        # Basic endpoints
        endpoints = [
            {"path": "/", "method": "GET", "name": "root"},
            {"path": "/health", "method": "GET", "name": "health"},
            {"path": "/makeup-types", "method": "GET", "name": "makeup_types"},
            {"path": "/api/color-recommendations?skin_tone=Monk05", "method": "GET", "name": "color_recommendations"},
            {"path": "/monitoring/metrics", "method": "GET", "name": "metrics"},
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    response = await client.request(
                        endpoint["method"],
                        f"{self.base_url}{endpoint['path']}",
                        timeout=10.0
                    )
                    duration = time.time() - start_time
                    
                    results[endpoint["name"]] = {
                        "status_code": response.status_code,
                        "response_time_ms": round(duration * 1000, 2),
                        "success": response.status_code < 400,
                        "headers": dict(response.headers),
                        "path": endpoint["path"]
                    }
                    
                except Exception as e:
                    results[endpoint["name"]] = {
                        "error": str(e),
                        "success": False,
                        "path": endpoint["path"]
                    }
        
        return results

class APILoadTester:
    """Simple load testing for API endpoints"""
    
    @staticmethod
    async def load_test_endpoint(url: str, concurrent_requests: int = 10, total_requests: int = 100):
        """Run load test on specific endpoint"""
        results = []
        
        async def make_request(client, semaphore):
            async with semaphore:
                try:
                    start_time = time.time()
                    response = await client.get(url)
                    duration = time.time() - start_time
                    
                    return {
                        "status_code": response.status_code,
                        "response_time": duration,
                        "success": response.status_code < 400
                    }
                except Exception as e:
                    return {
                        "error": str(e),
                        "success": False
                    }
        
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async with httpx.AsyncClient() as client:
            tasks = [make_request(client, semaphore) for _ in range(total_requests)]
            results = await asyncio.gather(*tasks)
        
        # Calculate statistics
        successful = [r for r in results if r.get("success", False)]
        response_times = [r["response_time"] for r in successful if "response_time" in r]
        
        return {
            "total_requests": total_requests,
            "successful_requests": len(successful),
            "failed_requests": total_requests - len(successful),
            "success_rate": len(successful) / total_requests * 100,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0
        }

class RequestResponseLogger(BaseHTTPMiddleware):
    """Middleware to log all API requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"API Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"API Response: {request.method} {request.url} -> "
            f"{response.status_code} ({process_time:.3f}s)"
        )
        
        # Add response time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class APIValidator:
    """Validate API responses against expected schemas"""
    
    @staticmethod
    def validate_color_recommendation_response(response_data: Dict) -> Dict[str, Any]:
        """Validate color recommendation API response"""
        errors = []
        
        # Check required fields
        if "colors_that_suit" not in response_data:
            errors.append("Missing 'colors_that_suit' field")
        elif not isinstance(response_data["colors_that_suit"], list):
            errors.append("'colors_that_suit' must be a list")
        else:
            # Validate color items
            for i, color in enumerate(response_data["colors_that_suit"]):
                if not isinstance(color, dict):
                    errors.append(f"Color item {i} must be a dictionary")
                    continue
                
                if "name" not in color:
                    errors.append(f"Color item {i} missing 'name' field")
                if "hex" not in color:
                    errors.append(f"Color item {i} missing 'hex' field")
                elif not color["hex"].startswith("#"):
                    errors.append(f"Color item {i} hex code must start with #")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

class ErrorRateMonitor:
    """Monitor API error rates"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.requests = []
    
    def record_request(self, success: bool):
        """Record a request result"""
        self.requests.append({
            "success": success,
            "timestamp": time.time()
        })
        
        # Keep only recent requests
        if len(self.requests) > self.window_size:
            self.requests = self.requests[-self.window_size:]
    
    def get_error_rate(self) -> float:
        """Get current error rate percentage"""
        if not self.requests:
            return 0.0
        
        failed_requests = sum(1 for r in self.requests if not r["success"])
        return (failed_requests / len(self.requests)) * 100
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detailed error statistics"""
        if not self.requests:
            return {
                "total_requests": 0,
                "error_rate": 0.0,
                "successful_requests": 0,
                "failed_requests": 0
            }
        
        total = len(self.requests)
        failed = sum(1 for r in self.requests if not r["success"])
        successful = total - failed
        
        return {
            "total_requests": total,
            "error_rate": (failed / total) * 100,
            "successful_requests": successful,
            "failed_requests": failed,
            "window_size": self.window_size
        }

# Quick test functions
async def quick_api_test(base_url: str = "http://localhost:8000"):
    """Run quick API tests"""
    print(f"🧪 Running Quick API Tests for {base_url}")
    
    health_checker = APIHealthChecker(base_url)
    results = await health_checker.run_health_checks()
    
    print("\n📊 Health Check Results:")
    for name, result in results.items():
        status = "✅" if result.get("success", False) else "❌"
        print(f"{status} {name}: {result.get('status_code', 'ERROR')} "
              f"({result.get('response_time_ms', 0):.2f}ms)")
    
    return results

async def performance_test(base_url: str = "http://localhost:8000", endpoint: str = "/health"):
    """Run performance test"""
    print(f"🚀 Running Performance Test: {base_url}{endpoint}")
    
    results = await APILoadTester.load_test_endpoint(
        f"{base_url}{endpoint}",
        concurrent_requests=5,
        total_requests=50
    )
    
    print(f"📈 Performance Results:")
    print(f"  Success Rate: {results['success_rate']:.1f}%")
    print(f"  Avg Response Time: {results['avg_response_time']:.3f}s")
    print(f"  Min/Max: {results['min_response_time']:.3f}s / {results['max_response_time']:.3f}s")
    
    return results

if __name__ == "__main__":
    # Run quick tests
    asyncio.run(quick_api_test())
