"""
Centralized Logging Configuration
Provides consistent logging levels and formats across the application
"""
import logging
import logging.config
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import json
from enum import Enum
from dataclasses import dataclass
import traceback

class LogLevel(str, Enum):
    """Standardized logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(str, Enum):
    """Logging categories for better organization"""
    API = "api"
    DATABASE = "database"
    AUTH = "auth"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"
    EXTERNAL = "external"
    MONITORING = "monitoring"

@dataclass
class LogContext:
    """Standard context for log entries"""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    api_version: Optional[str] = None
    operation: Optional[str] = None
    category: LogCategory = LogCategory.SYSTEM
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "api_version": self.api_version,
            "operation": self.operation,
            "category": self.category.value
        }

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logging
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add context if available
        if hasattr(record, 'context') and record.context:
            if isinstance(record.context, LogContext):
                log_entry["context"] = record.context.to_dict()
            elif isinstance(record.context, dict):
                log_entry["context"] = record.context
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text',
                          'stack_info', 'context']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class ConsoleFormatter(logging.Formatter):
    """
    Human-readable formatter for console output
    """
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Add color for console output if supported
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET'] if color else ''
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Base format
        message = f"{color}[{timestamp}] {record.levelname:8} {record.name:20} | {record.getMessage()}{reset}"
        
        # Add context if available
        if hasattr(record, 'context') and record.context:
            if isinstance(record.context, LogContext):
                context_str = f" | Context: {record.context.category.value}"
                if record.context.operation:
                    context_str += f".{record.context.operation}"
                if record.context.request_id:
                    context_str += f" [{record.context.request_id[:8]}...]"
                message += context_str
        
        # Add exception info
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message

class LoggingManager:
    """
    Centralized logging configuration manager
    """
    
    def __init__(self):
        self.configured = False
        self.log_level = LogLevel.INFO
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        
    def configure_logging(self, 
                         level: LogLevel = LogLevel.INFO,
                         enable_structured_logging: bool = None,
                         log_file: Optional[str] = None) -> None:
        """
        Configure application-wide logging
        
        Args:
            level: Default logging level
            enable_structured_logging: Enable JSON structured logging (auto-detect if None)
            log_file: Optional log file path
        """
        self.log_level = level
        
        # Auto-detect structured logging preference
        if enable_structured_logging is None:
            # Use structured logging in production, console in development
            enable_structured_logging = self.environment == "production"
        
        # Build logging configuration
        config = self._build_logging_config(level, enable_structured_logging, log_file)
        
        # Apply configuration
        logging.config.dictConfig(config)
        
        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.value))
        
        self.configured = True
        
        # Log configuration success
        logger = logging.getLogger(__name__)
        logger.info(
            "Logging configured successfully",
            extra={"context": LogContext(
                category=LogCategory.SYSTEM,
                operation="configure_logging"
            )}
        )
    
    def _build_logging_config(self, level: LogLevel, structured: bool, log_file: Optional[str]) -> Dict[str, Any]:
        """Build logging configuration dictionary"""
        
        formatters = {
            "structured": {
                "()": StructuredFormatter
            },
            "console": {
                "()": ConsoleFormatter
            }
        }
        
        handlers = {
            "console": {
                "class": "logging.StreamHandler",
                "level": level.value,
                "formatter": "console" if not structured else "structured",
                "stream": "ext://sys.stdout"
            }
        }
        
        # Add file handler if specified
        if log_file:
            handlers["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level.value,
                "formatter": "structured",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        
        # Configure specific loggers
        loggers = {
            # FastAPI/Uvicorn loggers
            "uvicorn": {
                "level": "INFO" if level == LogLevel.DEBUG else "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO" if level == LogLevel.DEBUG else "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            
            # Database loggers
            "sqlalchemy.engine": {
                "level": "WARNING",  # Reduce SQL query noise
                "handlers": ["console"],
                "propagate": False
            },
            "alembic": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            
            # Application loggers
            "aifashion": {  # Main application logger
                "level": level.value,
                "handlers": ["console"] + (["file"] if log_file else []),
                "propagate": False
            },
            
            # External service loggers
            "httpx": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "requests": {
                "level": "WARNING", 
                "handlers": ["console"],
                "propagate": False
            }
        }
        
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "loggers": loggers,
            "root": {
                "level": level.value,
                "handlers": ["console"] + (["file"] if log_file else [])
            }
        }
    
    def get_logger(self, name: str, category: LogCategory = LogCategory.SYSTEM) -> 'ContextualLogger':
        """
        Get a contextual logger with consistent configuration
        
        Args:
            name: Logger name (usually __name__)
            category: Default logging category
            
        Returns:
            Configured contextual logger
        """
        if not self.configured:
            self.configure_logging()
        
        base_logger = logging.getLogger(name)
        return ContextualLogger(base_logger, category)

class ContextualLogger:
    """
    Logger wrapper that adds consistent context to all log entries
    """
    
    def __init__(self, logger: logging.Logger, default_category: LogCategory = LogCategory.SYSTEM):
        self.logger = logger
        self.default_category = default_category
        self.default_context = LogContext(category=default_category)
    
    def _log(self, level: int, message: str, context: Optional[LogContext] = None, 
             exception: Optional[Exception] = None, **kwargs):
        """Internal logging method with context"""
        
        # Merge contexts
        final_context = self.default_context
        if context:
            # Create new context merging default and provided
            final_context = LogContext(
                user_id=context.user_id or self.default_context.user_id,
                request_id=context.request_id or self.default_context.request_id,
                session_id=context.session_id or self.default_context.session_id,
                api_version=context.api_version or self.default_context.api_version,
                operation=context.operation or self.default_context.operation,
                category=context.category if context.category != LogCategory.SYSTEM else self.default_context.category
            )
        
        # Add context to extra
        extra = kwargs.copy()
        extra["context"] = final_context
        
        # Log with exception info if provided
        exc_info = exception if exception else None
        self.logger.log(level, message, exc_info=exc_info, extra=extra)
    
    def debug(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, context, **kwargs)
    
    def info(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, context, **kwargs)
    
    def warning(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, context, **kwargs)
    
    def error(self, message: str, context: Optional[LogContext] = None, exception: Optional[Exception] = None, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, message, context, exception, **kwargs)
    
    def critical(self, message: str, context: Optional[LogContext] = None, exception: Optional[Exception] = None, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, message, context, exception, **kwargs)
    
    # Category-specific convenience methods
    def api_info(self, message: str, operation: str, request_id: Optional[str] = None, **kwargs):
        """Log API-related info"""
        context = LogContext(category=LogCategory.API, operation=operation, request_id=request_id)
        self.info(message, context, **kwargs)
    
    def api_error(self, message: str, operation: str, exception: Optional[Exception] = None, **kwargs):
        """Log API-related error"""
        context = LogContext(category=LogCategory.API, operation=operation)
        self.error(message, context, exception, **kwargs)
    
    def db_info(self, message: str, operation: str, **kwargs):
        """Log database-related info"""
        context = LogContext(category=LogCategory.DATABASE, operation=operation)
        self.info(message, context, **kwargs)
    
    def db_error(self, message: str, operation: str, exception: Optional[Exception] = None, **kwargs):
        """Log database-related error"""
        context = LogContext(category=LogCategory.DATABASE, operation=operation)
        self.error(message, context, exception, **kwargs)
    
    def performance_info(self, message: str, operation: str, duration_ms: Optional[float] = None, **kwargs):
        """Log performance-related info"""
        context = LogContext(category=LogCategory.PERFORMANCE, operation=operation)
        extra_data = kwargs.copy()
        if duration_ms:
            extra_data["duration_ms"] = duration_ms
        self.info(message, context, **extra_data)
    
    def security_warning(self, message: str, operation: str, **kwargs):
        """Log security-related warning"""
        context = LogContext(category=LogCategory.SECURITY, operation=operation)
        self.warning(message, context, **kwargs)
    
    def business_info(self, message: str, operation: str, user_id: Optional[str] = None, **kwargs):
        """Log business logic info"""
        context = LogContext(category=LogCategory.BUSINESS, operation=operation, user_id=user_id)
        self.info(message, context, **kwargs)

# Global logging manager
logging_manager = LoggingManager()

def get_logger(name: str, category: LogCategory = LogCategory.SYSTEM) -> ContextualLogger:
    """
    Get a configured logger
    
    Args:
        name: Logger name (usually __name__)
        category: Default logging category
        
    Returns:
        Configured contextual logger
    """
    return logging_manager.get_logger(name, category)

def configure_logging(level: LogLevel = LogLevel.INFO, 
                     enable_structured_logging: bool = None,
                     log_file: Optional[str] = None) -> None:
    """
    Configure application-wide logging
    
    Args:
        level: Default logging level
        enable_structured_logging: Enable JSON structured logging
        log_file: Optional log file path
    """
    logging_manager.configure_logging(level, enable_structured_logging, log_file)

# Standard logging strategies by category
class LoggingStrategies:
    """
    Standardized logging patterns for different scenarios
    """
    
    @staticmethod
    def log_api_request(logger: ContextualLogger, method: str, path: str, 
                       request_id: str, user_id: Optional[str] = None):
        """Log incoming API request"""
        context = LogContext(
            category=LogCategory.API,
            operation="request",
            request_id=request_id,
            user_id=user_id
        )
        logger.info(f"{method} {path}", context, method=method, path=path)
    
    @staticmethod
    def log_api_response(logger: ContextualLogger, method: str, path: str,
                        status_code: int, duration_ms: float, request_id: str):
        """Log API response"""
        level_method = logger.info if status_code < 400 else logger.error
        context = LogContext(
            category=LogCategory.API,
            operation="response", 
            request_id=request_id
        )
        level_method(
            f"{method} {path} -> {status_code}",
            context,
            status_code=status_code,
            duration_ms=duration_ms
        )
    
    @staticmethod
    def log_database_operation(logger: ContextualLogger, operation: str, 
                             table: str, duration_ms: Optional[float] = None,
                             success: bool = True):
        """Log database operation"""
        context = LogContext(category=LogCategory.DATABASE, operation=operation)
        message = f"Database {operation} on {table}"
        
        extra = {"table": table}
        if duration_ms:
            extra["duration_ms"] = duration_ms
        
        if success:
            logger.info(message, context, **extra)
        else:
            logger.error(f"{message} failed", context, **extra)
    
    @staticmethod
    def log_external_service_call(logger: ContextualLogger, service: str,
                                 operation: str, success: bool, duration_ms: float):
        """Log external service call"""
        context = LogContext(category=LogCategory.EXTERNAL, operation=operation)
        message = f"External service call: {service}.{operation}"
        
        extra = {"service": service, "duration_ms": duration_ms}
        
        if success:
            logger.info(message, context, **extra)
        else:
            logger.error(f"{message} failed", context, **extra)
    
    @staticmethod
    def log_security_event(logger: ContextualLogger, event_type: str, 
                          user_id: Optional[str] = None, details: Optional[Dict] = None):
        """Log security-related event"""
        context = LogContext(
            category=LogCategory.SECURITY,
            operation=event_type,
            user_id=user_id
        )
        message = f"Security event: {event_type}"
        
        extra = details or {}
        logger.warning(message, context, **extra)
