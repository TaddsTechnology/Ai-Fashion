"""
Health Monitoring and Performance Metrics for AI Fashion Backend
Provides comprehensive monitoring, health checks, and performance metrics.
"""

import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import asyncio
from cache_manager import cache_manager, check_cache_health
from async_database import async_db_service, monitor_connection_pool

logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
active_connections = Gauge('active_database_connections', 'Active database connections')
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate percentage')
image_processing_duration = Histogram('image_processing_duration_seconds', 'Image processing duration')
skin_tone_analysis_success_rate = Gauge('skin_tone_analysis_success_rate', 'Skin tone analysis success rate')

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    timestamp: datetime

@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""
    total_requests: int
    active_sessions: int
    cache_hit_rate: float
    database_connections: int
    average_response_time: float
    error_rate: float
    timestamp: datetime

@dataclass
class HealthStatus:
    """Overall health status"""
    status: str  # "healthy", "degraded", "unhealthy"
    components: Dict[str, Dict[str, Any]]
    timestamp: datetime
    uptime_seconds: float

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_times: List[float] = []
        self.error_count = 0
        self.total_requests = 0
        
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        request_count.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        
        self.total_requests += 1
        self.request_times.append(duration)
        
        # Keep only last 1000 request times for memory efficiency
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
        
        if status_code >= 400:
            self.error_count += 1
    
    def record_image_processing(self, duration: float):
        """Record image processing metrics"""
        image_processing_duration.observe(duration)
    
    def record_skin_tone_analysis(self, success: bool):
        """Record skin tone analysis metrics"""
        if success:
            skin_tone_analysis_success_rate.set(1)
        else:
            skin_tone_analysis_success_rate.set(0)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024 * 1024)
            network_recv_mb = network.bytes_recv / (1024 * 1024)
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_gb=memory.available / (1024**3),
                disk_usage_percent=disk_percent,
                network_io_sent_mb=network_sent_mb,
                network_io_recv_mb=network_recv_mb,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_gb=0.0,
                disk_usage_percent=0.0,
                network_io_sent_mb=0.0,
                network_io_recv_mb=0.0,
                timestamp=datetime.utcnow()
            )
    
    def get_application_metrics(self) -> ApplicationMetrics:
        """Get current application performance metrics"""
        try:
            # Calculate cache hit rate
            cache_stats = cache_manager.get_stats()
            if isinstance(cache_stats, dict) and "keyspace_hits" in cache_stats:
                hits = cache_stats.get("keyspace_hits", 0)
                misses = cache_stats.get("keyspace_misses", 0)
                total = hits + misses
                hit_rate = (hits / total * 100) if total > 0 else 0
                cache_hit_rate.set(hit_rate)
            else:
                hit_rate = 0.0
            
            # Calculate average response time
            avg_response_time = sum(self.request_times) / len(self.request_times) if self.request_times else 0.0
            
            # Calculate error rate
            error_rate = (self.error_count / self.total_requests * 100) if self.total_requests > 0 else 0.0
            
            return ApplicationMetrics(
                total_requests=self.total_requests,
                active_sessions=0,  # This would come from session management
                cache_hit_rate=hit_rate,
                database_connections=0,  # This would come from database pool
                average_response_time=avg_response_time,
                error_rate=error_rate,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return ApplicationMetrics(
                total_requests=0,
                active_sessions=0,
                cache_hit_rate=0.0,
                database_connections=0,
                average_response_time=0.0,
                error_rate=0.0,
                timestamp=datetime.utcnow()
            )
    
    async def get_health_status(self) -> HealthStatus:
        """Get comprehensive health status"""
        components = {}
        overall_status = "healthy"
        
        # Check cache health
        try:
            cache_health = check_cache_health()
            components["cache"] = cache_health
            if cache_health.get("status") != "healthy":
                overall_status = "degraded"
        except Exception as e:
            components["cache"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "unhealthy"
        
        # Check database health
        try:
            db_health = await async_db_service.health_check()
            components["database"] = db_health
            if db_health.get("status") != "healthy":
                overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
        except Exception as e:
            components["database"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "unhealthy"
        
        # Check system resources
        try:
            system_metrics = self.get_system_metrics()
            system_status = "healthy"
            
            if system_metrics.cpu_percent > 90:
                system_status = "degraded"
                overall_status = "degraded" if overall_status == "healthy" else overall_status
            elif system_metrics.cpu_percent > 95:
                system_status = "unhealthy"
                overall_status = "unhealthy"
            
            if system_metrics.memory_percent > 90:
                system_status = "degraded"
                overall_status = "degraded" if overall_status == "healthy" else overall_status
            elif system_metrics.memory_percent > 95:
                system_status = "unhealthy"
                overall_status = "unhealthy"
            
            components["system"] = {
                "status": system_status,
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "disk_usage_percent": system_metrics.disk_usage_percent
            }
        except Exception as e:
            components["system"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "unhealthy"
        
        # Check application metrics
        try:
            app_metrics = self.get_application_metrics()
            app_status = "healthy"
            
            if app_metrics.error_rate > 10:  # >10% error rate
                app_status = "degraded"
                overall_status = "degraded" if overall_status == "healthy" else overall_status
            elif app_metrics.error_rate > 25:  # >25% error rate
                app_status = "unhealthy"
                overall_status = "unhealthy"
            
            if app_metrics.average_response_time > 5.0:  # >5s average response time
                app_status = "degraded"
                overall_status = "degraded" if overall_status == "healthy" else overall_status
            
            components["application"] = {
                "status": app_status,
                "error_rate": app_metrics.error_rate,
                "average_response_time": app_metrics.average_response_time,
                "total_requests": app_metrics.total_requests
            }
        except Exception as e:
            components["application"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "unhealthy"
        
        uptime = time.time() - self.start_time
        
        return HealthStatus(
            status=overall_status,
            components=components,
            timestamp=datetime.utcnow(),
            uptime_seconds=uptime
        )

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

class HealthCheckManager:
    """Manages health checks and alerting"""
    
    def __init__(self):
        self.alert_thresholds = {
            "cpu_percent": 90,
            "memory_percent": 90,
            "disk_usage_percent": 85,
            "error_rate": 15,
            "average_response_time": 3.0
        }
        self.last_alerts = {}
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks and return results"""
        health_status = await performance_monitor.get_health_status()
        system_metrics = performance_monitor.get_system_metrics()
        app_metrics = performance_monitor.get_application_metrics()
        
        # Check for alerts
        alerts = self.check_alerts(system_metrics, app_metrics)
        
        return {
            "health": asdict(health_status),
            "system_metrics": asdict(system_metrics),
            "application_metrics": asdict(app_metrics),
            "alerts": alerts
        }
    
    def check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        current_time = datetime.utcnow()
        
        # CPU alert
        if system_metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
            alert_key = "high_cpu"
            if self.should_send_alert(alert_key, current_time):
                alerts.append({
                    "type": "high_cpu",
                    "severity": "warning" if system_metrics.cpu_percent < 95 else "critical",
                    "message": f"High CPU usage: {system_metrics.cpu_percent:.1f}%",
                    "value": system_metrics.cpu_percent,
                    "threshold": self.alert_thresholds["cpu_percent"],
                    "timestamp": current_time.isoformat()
                })
                self.last_alerts[alert_key] = current_time
        
        # Memory alert
        if system_metrics.memory_percent > self.alert_thresholds["memory_percent"]:
            alert_key = "high_memory"
            if self.should_send_alert(alert_key, current_time):
                alerts.append({
                    "type": "high_memory",
                    "severity": "warning" if system_metrics.memory_percent < 95 else "critical",
                    "message": f"High memory usage: {system_metrics.memory_percent:.1f}%",
                    "value": system_metrics.memory_percent,
                    "threshold": self.alert_thresholds["memory_percent"],
                    "timestamp": current_time.isoformat()
                })
                self.last_alerts[alert_key] = current_time
        
        # Disk alert
        if system_metrics.disk_usage_percent > self.alert_thresholds["disk_usage_percent"]:
            alert_key = "high_disk"
            if self.should_send_alert(alert_key, current_time):
                alerts.append({
                    "type": "high_disk_usage",
                    "severity": "warning" if system_metrics.disk_usage_percent < 95 else "critical",
                    "message": f"High disk usage: {system_metrics.disk_usage_percent:.1f}%",
                    "value": system_metrics.disk_usage_percent,
                    "threshold": self.alert_thresholds["disk_usage_percent"],
                    "timestamp": current_time.isoformat()
                })
                self.last_alerts[alert_key] = current_time
        
        # Error rate alert
        if app_metrics.error_rate > self.alert_thresholds["error_rate"]:
            alert_key = "high_error_rate"
            if self.should_send_alert(alert_key, current_time):
                alerts.append({
                    "type": "high_error_rate",
                    "severity": "warning" if app_metrics.error_rate < 25 else "critical",
                    "message": f"High error rate: {app_metrics.error_rate:.1f}%",
                    "value": app_metrics.error_rate,
                    "threshold": self.alert_thresholds["error_rate"],
                    "timestamp": current_time.isoformat()
                })
                self.last_alerts[alert_key] = current_time
        
        # Response time alert
        if app_metrics.average_response_time > self.alert_thresholds["average_response_time"]:
            alert_key = "slow_response"
            if self.should_send_alert(alert_key, current_time):
                alerts.append({
                    "type": "slow_response_time",
                    "severity": "warning" if app_metrics.average_response_time < 5.0 else "critical",
                    "message": f"Slow response time: {app_metrics.average_response_time:.2f}s",
                    "value": app_metrics.average_response_time,
                    "threshold": self.alert_thresholds["average_response_time"],
                    "timestamp": current_time.isoformat()
                })
                self.last_alerts[alert_key] = current_time
        
        return alerts
    
    def should_send_alert(self, alert_key: str, current_time: datetime) -> bool:
        """Check if we should send an alert (avoid spam)"""
        if alert_key not in self.last_alerts:
            return True
        
        # Send alert at most once every 5 minutes
        time_since_last = current_time - self.last_alerts[alert_key]
        return time_since_last > timedelta(minutes=5)

# Global health check manager
health_check_manager = HealthCheckManager()

# Middleware for request monitoring
class RequestMonitoringMiddleware:
    """Middleware to monitor HTTP requests"""
    
    def __init__(self):
        self.start_times = {}
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        request_id = id(request)
        self.start_times[request_id] = start_time
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record metrics
            method = request.method
            endpoint = request.url.path
            status_code = response.status_code
            
            performance_monitor.record_request(method, endpoint, status_code, duration)
            
            # Clean up
            self.start_times.pop(request_id, None)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            performance_monitor.record_request(request.method, request.url.path, 500, duration)
            self.start_times.pop(request_id, None)
            raise

# Endpoints for monitoring
async def get_health_endpoint() -> Dict[str, Any]:
    """Health check endpoint"""
    return await health_check_manager.run_health_checks()

async def get_metrics_endpoint() -> Response:
    """Prometheus metrics endpoint"""
    try:
        # Update gauges with current values
        system_metrics = performance_monitor.get_system_metrics()
        app_metrics = performance_monitor.get_application_metrics()
        
        # Update database connections gauge
        try:
            pool_stats = await monitor_connection_pool()
            active_connections.set(pool_stats.get("checked_out_connections", 0))
        except Exception:
            pass
        
        # Generate Prometheus metrics
        metrics_output = generate_latest()
        return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
        
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return Response(content="", media_type=CONTENT_TYPE_LATEST, status_code=500)

async def get_system_stats_endpoint() -> Dict[str, Any]:
    """System statistics endpoint"""
    try:
        system_metrics = performance_monitor.get_system_metrics()
        app_metrics = performance_monitor.get_application_metrics()
        
        # Get additional stats
        cache_stats = cache_manager.get_stats()
        db_stats = await async_db_service.get_database_stats()
        
        return {
            "system": asdict(system_metrics),
            "application": asdict(app_metrics),
            "cache": cache_stats,
            "database": db_stats,
            "uptime_seconds": time.time() - performance_monitor.start_time
        }
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return {"error": str(e)}

# Background monitoring tasks
async def periodic_health_check():
    """Periodic health check task"""
    while True:
        try:
            await health_check_manager.run_health_checks()
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error in periodic health check: {e}")
            await asyncio.sleep(60)

async def cleanup_old_metrics():
    """Cleanup old metrics data"""
    while True:
        try:
            # Clean up old request times (keep only last hour)
            current_time = time.time()
            if len(performance_monitor.request_times) > 3600:  # Assume 1 req/sec max
                performance_monitor.request_times = performance_monitor.request_times[-3600:]
            
            await asyncio.sleep(3600)  # Clean up every hour
        except Exception as e:
            logger.error(f"Error in metrics cleanup: {e}")
            await asyncio.sleep(3600)
