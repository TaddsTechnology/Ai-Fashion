"""
Enhanced Monitoring System for AI Fashion Backend

Addresses all monitoring issues:
1. Advanced metrics collection and aggregation
2. Automated alerting configuration with multiple channels
3. Request tracing and correlation IDs
4. Complete health checks with dependency verification
5. Performance monitoring and anomaly detection
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import threading
from contextlib import asynccontextmanager

import psutil
from fastapi import Request, Response, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts"""
    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CUSTOM = "custom"


@dataclass
class MetricData:
    """Metric data container"""
    name: str
    description: str
    type: MetricType
    unit: str = ""
    help_text: str = ""
    labels: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    values: Dict[str, List[Tuple[float, float]]] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    description: str
    type: AlertType
    severity: AlertSeverity
    query: str
    threshold: float
    comparator: str  # "gt", "lt", "eq", "ne"
    duration_seconds: int
    enabled: bool = True
    silenced_until: Optional[float] = None
    last_triggered: Optional[float] = None
    count: int = 0


@dataclass
class AlertEvent:
    """Alert event triggered by condition"""
    alert_id: str
    alert_name: str
    alert_type: str
    severity: str
    value: float
    threshold: float
    timestamp: float
    message: str
    comparator: str
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Span:
    """Request tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status: str = "ok"  # "ok", "error", "timeout", "cancelled"
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Trace:
    """Complete trace consisting of spans"""
    trace_id: str
    spans: List[Span] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    name: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsRegistry:
    """Central registry for application metrics"""
    
    def __init__(self, max_points_per_metric: int = 1000):
        self.metrics: Dict[str, MetricData] = {}
        self.max_points = max_points_per_metric
        self._lock = threading.Lock()
    
    def create_counter(self, name: str, description: str, unit: str = "", labels: List[str] = None) -> str:
        """Create a counter metric"""
        with self._lock:
            if name in self.metrics:
                return name
            
            self.metrics[name] = MetricData(
                name=name,
                description=description,
                type=MetricType.COUNTER,
                unit=unit,
                labels=labels or []
            )
            return name
    
    def create_gauge(self, name: str, description: str, unit: str = "", labels: List[str] = None) -> str:
        """Create a gauge metric"""
        with self._lock:
            if name in self.metrics:
                return name
            
            self.metrics[name] = MetricData(
                name=name,
                description=description,
                type=MetricType.GAUGE,
                unit=unit,
                labels=labels or []
            )
            return name
    
    def create_histogram(self, name: str, description: str, unit: str = "", labels: List[str] = None) -> str:
        """Create a histogram metric"""
        with self._lock:
            if name in self.metrics:
                return name
            
            self.metrics[name] = MetricData(
                name=name,
                description=description,
                type=MetricType.HISTOGRAM,
                unit=unit,
                labels=labels or []
            )
            return name
    
    def increment(self, name: str, value: float = 1.0, labels: Dict[str, str] = None) -> None:
        """Increment a counter metric"""
        with self._lock:
            if name not in self.metrics:
                self.create_counter(name, f"Auto-created counter: {name}")
            
            metric = self.metrics[name]
            if metric.type != MetricType.COUNTER:
                logger.warning(f"Attempted to increment non-counter metric: {name}")
                return
            
            label_key = self._get_label_key(labels or {})
            if label_key not in metric.values:
                metric.values[label_key] = []
            
            # For counters, we add to the last value
            last_value = 0
            if metric.values[label_key]:
                _, last_value = metric.values[label_key][-1]
            
            new_value = last_value + value
            metric.values[label_key].append((time.time(), new_value))
            
            # Trim if needed
            if len(metric.values[label_key]) > self.max_points:
                metric.values[label_key] = metric.values[label_key][-self.max_points:]
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set a gauge metric"""
        with self._lock:
            if name not in self.metrics:
                self.create_gauge(name, f"Auto-created gauge: {name}")
            
            metric = self.metrics[name]
            if metric.type != MetricType.GAUGE:
                logger.warning(f"Attempted to set non-gauge metric: {name}")
                return
            
            label_key = self._get_label_key(labels or {})
            if label_key not in metric.values:
                metric.values[label_key] = []
            
            metric.values[label_key].append((time.time(), value))
            
            # Trim if needed
            if len(metric.values[label_key]) > self.max_points:
                metric.values[label_key] = metric.values[label_key][-self.max_points:]
    
    def observe(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Observe a value for a histogram metric"""
        with self._lock:
            if name not in self.metrics:
                self.create_histogram(name, f"Auto-created histogram: {name}")
            
            metric = self.metrics[name]
            if metric.type != MetricType.HISTOGRAM:
                logger.warning(f"Attempted to observe non-histogram metric: {name}")
                return
            
            label_key = self._get_label_key(labels or {})
            if label_key not in metric.values:
                metric.values[label_key] = []
            
            metric.values[label_key].append((time.time(), value))
            
            # Trim if needed
            if len(metric.values[label_key]) > self.max_points:
                metric.values[label_key] = metric.values[label_key][-self.max_points:]
    
    def get_metric(self, name: str) -> Optional[MetricData]:
        """Get a metric by name"""
        with self._lock:
            return self.metrics.get(name)
    
    def get_metric_values(self, name: str, labels: Dict[str, str] = None, 
                          since: Optional[float] = None) -> List[Tuple[float, float]]:
        """Get values for a metric"""
        with self._lock:
            if name not in self.metrics:
                return []
            
            metric = self.metrics[name]
            label_key = self._get_label_key(labels or {})
            
            if label_key not in metric.values:
                return []
            
            values = metric.values[label_key]
            
            if since is not None:
                values = [(ts, val) for ts, val in values if ts >= since]
            
            return values
    
    def get_metric_summary(self, name: str, labels: Dict[str, str] = None,
                           since: Optional[float] = None) -> Dict[str, Any]:
        """Get statistical summary for a metric"""
        values = self.get_metric_values(name, labels, since)
        
        if not values:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "sum": None,
                "last": None
            }
        
        just_values = [v for _, v in values]
        
        return {
            "count": len(values),
            "min": min(just_values),
            "max": max(just_values),
            "avg": sum(just_values) / len(just_values),
            "sum": sum(just_values),
            "last": just_values[-1]
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all metrics with their summaries"""
        result = {}
        
        with self._lock:
            for name, metric in self.metrics.items():
                metric_info = {
                    "name": metric.name,
                    "description": metric.description,
                    "type": metric.type.value,
                    "unit": metric.unit,
                    "labels": {}
                }
                
                # Get summaries for each label set
                for label_key, values in metric.values.items():
                    if not values:
                        continue
                    
                    labels = self._parse_label_key(label_key)
                    just_values = [v for _, v in values]
                    
                    metric_info["labels"][label_key] = {
                        "labels": labels,
                        "count": len(values),
                        "min": min(just_values),
                        "max": max(just_values),
                        "avg": sum(just_values) / len(just_values),
                        "last": just_values[-1],
                        "timestamp": values[-1][0]
                    }
                
                result[name] = metric_info
        
        return result
    
    def _get_label_key(self, labels: Dict[str, str]) -> str:
        """Generate a unique key for labels"""
        if not labels:
            return ""
        
        # Sort labels for consistent key
        sorted_items = sorted(labels.items())
        return json.dumps(sorted_items)
    
    def _parse_label_key(self, label_key: str) -> Dict[str, str]:
        """Parse a label key back to a dict"""
        if not label_key:
            return {}
        
        try:
            pairs = json.loads(label_key)
            return dict(pairs)
        except:
            return {}


class TraceManager:
    """Manages traces and spans for request tracing"""
    
    def __init__(self, max_traces: int = 1000):
        self.traces: Dict[str, Trace] = {}
        self.active_spans: Dict[str, Span] = {}
        self.max_traces = max_traces
        self._lock = threading.Lock()
    
    def start_trace(self, name: str, trace_id: Optional[str] = None) -> Tuple[str, str]:
        """Start a new trace and return trace_id, span_id"""
        trace_id = trace_id or str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        with self._lock:
            # Create new trace if needed
            if trace_id not in self.traces:
                self.traces[trace_id] = Trace(
                    trace_id=trace_id,
                    name=name,
                    start_time=time.time()
                )
            
            # Create root span
            span = Span(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=None,
                name=name,
                start_time=time.time()
            )
            
            self.traces[trace_id].spans.append(span)
            self.active_spans[span_id] = span
            
            # Clean up old traces if needed
            if len(self.traces) > self.max_traces:
                oldest_trace_id = min(self.traces.keys(), 
                                     key=lambda tid: self.traces[tid].start_time)
                self._cleanup_trace(oldest_trace_id)
        
        return trace_id, span_id
    
    def start_span(self, name: str, parent_span_id: Optional[str] = None,
                  trace_id: Optional[str] = None) -> str:
        """Start a new span in existing trace or create a new trace"""
        # If parent_span_id is provided, use its trace_id
        if parent_span_id:
            with self._lock:
                parent_span = self.active_spans.get(parent_span_id)
                if parent_span:
                    trace_id = parent_span.trace_id
                else:
                    # Parent not found, start a new trace
                    trace_id, span_id = self.start_trace(name, trace_id)
                    return span_id
        
        # If no parent and no trace_id, start a new trace
        if not trace_id:
            trace_id, span_id = self.start_trace(name)
            return span_id
        
        # Create span in existing trace
        span_id = str(uuid.uuid4())
        
        with self._lock:
            if trace_id not in self.traces:
                # Trace not found, start a new one
                trace_id, span_id = self.start_trace(name, trace_id)
                return span_id
            
            span = Span(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                name=name,
                start_time=time.time()
            )
            
            self.traces[trace_id].spans.append(span)
            self.active_spans[span_id] = span
        
        return span_id
    
    def end_span(self, span_id: str, status: str = "ok", tags: Dict[str, str] = None) -> None:
        """End an active span"""
        with self._lock:
            span = self.active_spans.get(span_id)
            if not span:
                logger.warning(f"Attempted to end non-existent span: {span_id}")
                return
            
            span.end_time = time.time()
            span.duration_ms = (span.end_time - span.start_time) * 1000
            span.status = status
            
            if tags:
                span.tags.update(tags)
            
            # Remove from active spans
            self.active_spans.pop(span_id, None)
    
    def add_span_tag(self, span_id: str, key: str, value: str) -> None:
        """Add a tag to a span"""
        with self._lock:
            span = self.active_spans.get(span_id)
            if not span:
                logger.warning(f"Attempted to tag non-existent span: {span_id}")
                return
            
            span.tags[key] = value
    
    def add_span_log(self, span_id: str, event: str, payload: Dict[str, Any] = None) -> None:
        """Add a log entry to a span"""
        with self._lock:
            span = self.active_spans.get(span_id)
            if not span:
                logger.warning(f"Attempted to log to non-existent span: {span_id}")
                return
            
            log_entry = {
                "timestamp": time.time(),
                "event": event
            }
            
            if payload:
                log_entry["payload"] = payload
            
            span.logs.append(log_entry)
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID"""
        with self._lock:
            return self.traces.get(trace_id)
    
    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a trace"""
        trace = self.get_trace(trace_id)
        if not trace:
            return None
        
        spans = trace.spans
        if not spans:
            return {
                "trace_id": trace_id,
                "name": trace.name,
                "duration_ms": 0,
                "spans": 0,
                "status": "unknown",
                "start_time": trace.start_time,
                "errors": 0
            }
        
        # Calculate trace duration from the root span or the earliest span
        root_spans = [s for s in spans if s.parent_span_id is None]
        if root_spans:
            root_span = root_spans[0]
            start_time = root_span.start_time
            end_time = root_span.end_time or time.time()
        else:
            start_time = min(s.start_time for s in spans)
            end_times = [s.end_time for s in spans if s.end_time is not None]
            end_time = max(end_times) if end_times else time.time()
        
        duration_ms = (end_time - start_time) * 1000
        error_spans = [s for s in spans if s.status == "error"]
        
        return {
            "trace_id": trace_id,
            "name": trace.name or (root_spans[0].name if root_spans else "unknown"),
            "duration_ms": duration_ms,
            "spans": len(spans),
            "status": "error" if error_spans else "ok",
            "start_time": start_time,
            "errors": len(error_spans),
            "tags": trace.tags
        }
    
    def get_recent_traces(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get summaries of recent traces"""
        with self._lock:
            # Sort traces by start time (newest first)
            trace_ids = sorted(
                self.traces.keys(),
                key=lambda tid: self.traces[tid].start_time,
                reverse=True
            )
            
            summaries = []
            for trace_id in trace_ids[:limit]:
                summary = self.get_trace_summary(trace_id)
                if summary:
                    summaries.append(summary)
            
            return summaries
    
    def _cleanup_trace(self, trace_id: str) -> None:
        """Clean up a trace and its spans"""
        if trace_id in self.traces:
            # Remove any active spans for this trace
            spans_to_remove = [
                span_id for span_id, span in self.active_spans.items()
                if span.trace_id == trace_id
            ]
            for span_id in spans_to_remove:
                self.active_spans.pop(span_id, None)
            
            # Remove the trace
            self.traces.pop(trace_id, None)


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, metrics_registry: MetricsRegistry):
        self.metrics = metrics_registry
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.notification_channels: List[Callable[[AlertEvent], None]] = []
        self._lock = threading.Lock()
    
    def register_alert(self, alert: Alert) -> None:
        """Register a new alert"""
        with self._lock:
            self.alerts[alert.id] = alert
    
    def register_notification_channel(self, channel: Callable[[AlertEvent], None]) -> None:
        """Register a notification channel"""
        self.notification_channels.append(channel)
    
    def check_alerts(self) -> List[AlertEvent]:
        """Check all alerts and return triggered alerts"""
        current_time = time.time()
        triggered_alerts = []
        
        with self._lock:
            for alert_id, alert in self.alerts.items():
                if not alert.enabled:
                    continue
                
                if alert.silenced_until and current_time < alert.silenced_until:
                    continue
                
                try:
                    # Simple query format: "metric_name{label1=value1,label2=value2}"
                    query_parts = alert.query.split("{", 1)
                    metric_name = query_parts[0].strip()
                    
                    labels = {}
                    if len(query_parts) > 1 and "}" in query_parts[1]:
                        labels_str = query_parts[1].split("}", 1)[0]
                        for label_pair in labels_str.split(","):
                            if "=" in label_pair:
                                key, value = label_pair.split("=", 1)
                                labels[key.strip()] = value.strip()
                    
                    # Get metric values
                    since = current_time - alert.duration_seconds
                    values = self.metrics.get_metric_values(metric_name, labels, since)
                    
                    if not values:
                        continue
                    
                    # Get the latest value
                    _, latest_value = values[-1]
                    
                    # Check condition
                    if self._check_condition(latest_value, alert.threshold, alert.comparator):
                        # Only trigger if this is a new alert or enough time has passed
                        if (alert.last_triggered is None or 
                            current_time - alert.last_triggered > 300):  # 5 minute cooldown
                            
                            alert.last_triggered = current_time
                            alert.count += 1
                            
                            event = AlertEvent(
                                alert_id=alert.id,
                                alert_name=alert.name,
                                alert_type=alert.type.value,
                                severity=alert.severity.value,
                                value=latest_value,
                                threshold=alert.threshold,
                                timestamp=current_time,
                                message=self._format_alert_message(alert, latest_value),
                                comparator=alert.comparator,
                                labels=labels
                            )
                            
                            triggered_alerts.append(event)
                            self.alert_history.append(event)
                            
                            # Notify channels
                            for channel in self.notification_channels:
                                try:
                                    channel(event)
                                except Exception as e:
                                    logger.error(f"Error in notification channel: {e}")
                    
                except Exception as e:
                    logger.error(f"Error checking alert {alert_id}: {e}")
        
        return triggered_alerts
    
    def silence_alert(self, alert_id: str, duration_seconds: int) -> bool:
        """Silence an alert for a duration"""
        with self._lock:
            alert = self.alerts.get(alert_id)
            if not alert:
                return False
            
            alert.silenced_until = time.time() + duration_seconds
            return True
    
    def get_alert_history(self, limit: int = 100) -> List[AlertEvent]:
        """Get recent alert history"""
        with self._lock:
            return list(self.alert_history)[-limit:]
    
    def _check_condition(self, value: float, threshold: float, comparator: str) -> bool:
        """Check if value meets condition"""
        if comparator == "gt":
            return value > threshold
        elif comparator == "lt":
            return value < threshold
        elif comparator == "eq":
            return value == threshold
        elif comparator == "ne":
            return value != threshold
        elif comparator == "ge":
            return value >= threshold
        elif comparator == "le":
            return value <= threshold
        else:
            logger.warning(f"Unknown comparator: {comparator}")
            return False
    
    def _format_alert_message(self, alert: Alert, value: float) -> str:
        """Format an alert message"""
        comparator_words = {
            "gt": "greater than",
            "lt": "less than",
            "eq": "equal to",
            "ne": "not equal to",
            "ge": "greater than or equal to",
            "le": "less than or equal to"
        }
        
        comparator_text = comparator_words.get(alert.comparator, alert.comparator)
        
        return (f"{alert.name}: {alert.description} - "
                f"Value {value} is {comparator_text} threshold {alert.threshold}")


class SystemMetricsCollector:
    """Collects system metrics periodically"""
    
    def __init__(self, metrics_registry: MetricsRegistry):
        self.metrics = metrics_registry
        self._running = False
        self._task = None
    
    async def start(self, interval_seconds: int = 60):
        """Start collecting metrics"""
        self._running = True
        self._task = asyncio.create_task(self._collect_loop(interval_seconds))
    
    async def stop(self):
        """Stop collecting metrics"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _collect_loop(self, interval_seconds: int):
        """Collection loop"""
        while self._running:
            try:
                self._collect_metrics()
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(interval_seconds)
    
    def _collect_metrics(self):
        """Collect all system metrics"""
        # CPU metrics
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.set_gauge("system_cpu_percent", cpu_percent)
            
            per_cpu = psutil.cpu_percent(interval=None, percpu=True)
            for i, percent in enumerate(per_cpu):
                self.metrics.set_gauge("system_cpu_core_percent", percent, {"core": str(i)})
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
        
        # Memory metrics
        try:
            memory = psutil.virtual_memory()
            self.metrics.set_gauge("system_memory_total_bytes", memory.total)
            self.metrics.set_gauge("system_memory_available_bytes", memory.available)
            self.metrics.set_gauge("system_memory_used_bytes", memory.used)
            self.metrics.set_gauge("system_memory_percent", memory.percent)
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
        
        # Disk metrics
        try:
            disk = psutil.disk_usage('/')
            self.metrics.set_gauge("system_disk_total_bytes", disk.total)
            self.metrics.set_gauge("system_disk_used_bytes", disk.used)
            self.metrics.set_gauge("system_disk_free_bytes", disk.free)
            self.metrics.set_gauge("system_disk_percent", disk.percent)
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
        
        # Network metrics
        try:
            net_io = psutil.net_io_counters()
            self.metrics.set_gauge("system_network_bytes_sent", net_io.bytes_sent)
            self.metrics.set_gauge("system_network_bytes_recv", net_io.bytes_recv)
            self.metrics.set_gauge("system_network_packets_sent", net_io.packets_sent)
            self.metrics.set_gauge("system_network_packets_recv", net_io.packets_recv)
            self.metrics.set_gauge("system_network_errin", net_io.errin)
            self.metrics.set_gauge("system_network_errout", net_io.errout)
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
        
        # Process metrics for current process
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            self.metrics.set_gauge("process_memory_rss_bytes", memory_info.rss)
            self.metrics.set_gauge("process_memory_vms_bytes", memory_info.vms)
            self.metrics.set_gauge("process_cpu_percent", process.cpu_percent())
            self.metrics.set_gauge("process_threads", process.num_threads())
            
            # File descriptors (Unix only)
            try:
                self.metrics.set_gauge("process_open_files", len(process.open_files()))
                self.metrics.set_gauge("process_open_connections", len(process.connections()))
            except (AttributeError, psutil.AccessDenied):
                pass
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics"""
    
    def __init__(
        self, 
        app: ASGIApp,
        metrics_registry: MetricsRegistry,
        trace_manager: TraceManager
    ):
        super().__init__(app)
        self.metrics = metrics_registry
        self.tracer = trace_manager
        
        # Create standard metrics
        self.metrics.create_counter(
            "http_requests_total", 
            "Total number of HTTP requests",
            labels=["method", "path", "endpoint"]
        )
        self.metrics.create_histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            labels=["method", "path", "endpoint"]
        )
        self.metrics.create_counter(
            "http_responses_total",
            "Total number of HTTP responses",
            labels=["method", "path", "status", "endpoint"]
        )
        self.metrics.create_counter(
            "http_errors_total",
            "Total number of HTTP errors",
            labels=["method", "path", "error_type", "endpoint"]
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics"""
        start_time = time.time()
        
        # Extract endpoint name for more useful metrics
        endpoint = self._get_endpoint_name(request.url.path)
        
        # Create trace for request
        trace_id = request.headers.get("X-Trace-ID")
        span_name = f"{request.method} {endpoint}"
        trace_id, span_id = self.tracer.start_trace(span_name, trace_id)
        
        # Add trace info to request state
        request.state.trace_id = trace_id
        request.state.span_id = span_id
        
        # Add request details to span
        self.tracer.add_span_tag(span_id, "http.method", request.method)
        self.tracer.add_span_tag(span_id, "http.url", str(request.url))
        self.tracer.add_span_tag(span_id, "http.path", request.url.path)
        
        # Increment request counter
        self.metrics.increment("http_requests_total", 1.0, {
            "method": request.method,
            "path": request.url.path,
            "endpoint": endpoint
        })
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record response metrics
            self.metrics.observe("http_request_duration_seconds", duration, {
                "method": request.method,
                "path": request.url.path,
                "endpoint": endpoint
            })
            
            self.metrics.increment("http_responses_total", 1.0, {
                "method": request.method,
                "path": request.url.path,
                "status": str(response.status_code),
                "endpoint": endpoint
            })
            
            # Finish span
            self.tracer.add_span_tag(span_id, "http.status_code", str(response.status_code))
            status = "ok" if response.status_code < 400 else "error"
            self.tracer.end_span(span_id, status)
            
            # Add trace headers to response
            response.headers["X-Trace-ID"] = trace_id
            
            return response
            
        except Exception as e:
            # Record error metrics
            self.metrics.increment("http_errors_total", 1.0, {
                "method": request.method,
                "path": request.url.path,
                "error_type": type(e).__name__,
                "endpoint": endpoint
            })
            
            # End span with error
            self.tracer.add_span_tag(span_id, "error", "true")
            self.tracer.add_span_tag(span_id, "error.message", str(e))
            self.tracer.add_span_tag(span_id, "error.type", type(e).__name__)
            self.tracer.end_span(span_id, "error")
            
            raise
    
    def _get_endpoint_name(self, path: str) -> str:
        """Extract a meaningful endpoint name from a path"""
        if path == "/":
            return "root"
        
        # Handle common API patterns
        if path.startswith("/api/"):
            parts = path.split("/")
            if len(parts) > 2:
                return f"api.{parts[2]}"
            return "api"
        
        # Remove path parameters for cleaner metrics
        parts = path.strip("/").split("/")
        # Replace numeric parts with {id}
        parts = ["{id}" if part.isdigit() else part for part in parts]
        return ".".join(parts)


class HealthCheck:
    """Health check system"""
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], Dict[str, Any]]] = {}
    
    def register_check(self, name: str, check_func: Callable[[], Dict[str, Any]]):
        """Register a health check"""
        self.checks[name] = check_func
    
    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_status = "healthy"
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                results[name] = result
                
                # Update overall status
                if result.get("status") == "unhealthy":
                    overall_status = "unhealthy"
                elif result.get("status") == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"
            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "checks": results,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global instances
metrics_registry = MetricsRegistry()
trace_manager = TraceManager()
alert_manager = AlertManager(metrics_registry)
system_metrics = SystemMetricsCollector(metrics_registry)
health_check = HealthCheck()


def _log_alert_channel(alert: AlertEvent):
    """Log alerts to the application logger"""
    severity_emoji = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "🔴",
        "critical": "🚨"
    }
    emoji = severity_emoji.get(alert.severity, "🔔")
    
    if alert.severity == "critical":
        logger.critical(
            f"{emoji} ALERT: {alert.alert_name} - {alert.message} "
            f"[{alert.value} {alert.comparator} {alert.threshold}]"
        )
    elif alert.severity == "error":
        logger.error(
            f"{emoji} ALERT: {alert.alert_name} - {alert.message} "
            f"[{alert.value} {alert.comparator} {alert.threshold}]"
        )
    elif alert.severity == "warning":
        logger.warning(
            f"{emoji} ALERT: {alert.alert_name} - {alert.message} "
            f"[{alert.value} {alert.comparator} {alert.threshold}]"
        )
    else:
        logger.info(
            f"{emoji} ALERT: {alert.alert_name} - {alert.message} "
            f"[{alert.value} {alert.comparator} {alert.threshold}]"
        )


def setup_default_alerts():
    """Setup default alerts"""
    # System alerts
    alert_manager.register_alert(Alert(
        id="high_cpu_usage",
        name="High CPU Usage",
        description="CPU usage is too high",
        type=AlertType.SYSTEM,
        severity=AlertSeverity.WARNING,
        query="system_cpu_percent",
        threshold=80.0,
        comparator="gt",
        duration_seconds=300  # 5 minutes
    ))
    
    alert_manager.register_alert(Alert(
        id="high_memory_usage",
        name="High Memory Usage",
        description="Memory usage is too high",
        type=AlertType.SYSTEM,
        severity=AlertSeverity.WARNING,
        query="system_memory_percent",
        threshold=85.0,
        comparator="gt",
        duration_seconds=300
    ))
    
    alert_manager.register_alert(Alert(
        id="high_disk_usage",
        name="High Disk Usage",
        description="Disk usage is too high",
        type=AlertType.SYSTEM,
        severity=AlertSeverity.WARNING,
        query="system_disk_percent",
        threshold=85.0,
        comparator="gt",
        duration_seconds=300
    ))
    
    # Application alerts
    alert_manager.register_alert(Alert(
        id="high_error_rate",
        name="High Error Rate",
        description="HTTP error rate is too high",
        type=AlertType.APPLICATION,
        severity=AlertSeverity.ERROR,
        query="http_errors_total",
        threshold=10.0,
        comparator="gt",
        duration_seconds=300
    ))
    
    alert_manager.register_alert(Alert(
        id="slow_response_time",
        name="Slow Response Time",
        description="HTTP response time is too high",
        type=AlertType.PERFORMANCE,
        severity=AlertSeverity.WARNING,
        query="http_request_duration_seconds",
        threshold=5.0,  # 5 seconds
        comparator="gt",
        duration_seconds=300
    ))


def setup_monitoring_middleware(app: FastAPI):
    """Setup monitoring middleware before application startup"""
    try:
        # Register middleware for request metrics
        app.add_middleware(
            RequestMetricsMiddleware,
            metrics_registry=metrics_registry,
            trace_manager=trace_manager
        )
        logger.info("📊 Monitoring middleware added")
    except Exception as e:
        logger.error(f"Failed to add monitoring middleware: {e}")
        raise

async def setup_monitoring(app: FastAPI):
    """Setup monitoring systems for a FastAPI app (excluding middleware)"""
    # Store references in app state
    app.state.metrics_registry = metrics_registry
    app.state.trace_manager = trace_manager
    app.state.alert_manager = alert_manager
    app.state.system_metrics = system_metrics
    app.state.health_check = health_check
    
    # Setup default notification channel
    alert_manager.register_notification_channel(_log_alert_channel)
    
    # Setup default alerts
    setup_default_alerts()
    
    # Start system metrics collection
    await system_metrics.start()
    
    # Start alert checking task
    asyncio.create_task(alert_checking_loop())
    
    logger.info("📊 Comprehensive monitoring system initialized")


async def cleanup_monitoring(app: FastAPI):
    """Cleanup monitoring resources"""
    # Stop system metrics collection
    if hasattr(app.state, 'system_metrics'):
        await app.state.system_metrics.stop()
    
    logger.info("📊 Monitoring system resources cleaned up")


async def alert_checking_loop():
    """Background task to check alerts periodically"""
    while True:
        try:
            alert_manager.check_alerts()
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error in alert checking loop: {e}")
            await asyncio.sleep(60)


def setup_database_health_check(check_func):
    """Setup database health check"""
    health_check.register_check("database", check_func)


def setup_cache_health_check(check_func):
    """Setup cache health check"""
    health_check.register_check("cache", check_func)


def setup_custom_health_check(name, check_func):
    """Setup a custom health check"""
    health_check.register_check(name, check_func)


# Utility functions for API endpoints
async def get_health_status():
    """Get health status for API endpoint"""
    return await health_check.run_checks()


def get_metrics():
    """Get metrics for API endpoint"""
    return metrics_registry.get_all_metrics()


def get_traces(limit=20):
    """Get recent traces for API endpoint"""
    return trace_manager.get_recent_traces(limit)


def get_trace_details(trace_id):
    """Get trace details for API endpoint"""
    trace = trace_manager.get_trace(trace_id)
    if not trace:
        return None
    
    return {
        "trace_id": trace.trace_id,
        "name": trace.name,
        "start_time": trace.start_time,
        "spans": [asdict(span) for span in trace.spans],
        "tags": trace.tags
    }


def get_alerts():
    """Get alerts for API endpoint"""
    return {
        "alerts": [asdict(alert) for alert in alert_manager.alerts.values()],
        "history": [asdict(event) for event in alert_manager.get_alert_history()]
    }


def get_system_stats():
    """Get system statistics for API endpoint"""
    return {
        "cpu": {
            "percent": metrics_registry.get_metric_summary("system_cpu_percent").get("last", 0)
        },
        "memory": {
            "percent": metrics_registry.get_metric_summary("system_memory_percent").get("last", 0),
            "total_gb": metrics_registry.get_metric_summary("system_memory_total_bytes").get("last", 0) / (1024**3),
            "used_gb": metrics_registry.get_metric_summary("system_memory_used_bytes").get("last", 0) / (1024**3)
        },
        "disk": {
            "percent": metrics_registry.get_metric_summary("system_disk_percent").get("last", 0),
            "total_gb": metrics_registry.get_metric_summary("system_disk_total_bytes").get("last", 0) / (1024**3),
            "used_gb": metrics_registry.get_metric_summary("system_disk_used_bytes").get("last", 0) / (1024**3)
        },
        "process": {
            "memory_rss_mb": metrics_registry.get_metric_summary("process_memory_rss_bytes").get("last", 0) / (1024**2),
            "cpu_percent": metrics_registry.get_metric_summary("process_cpu_percent").get("last", 0)
        }
    }
