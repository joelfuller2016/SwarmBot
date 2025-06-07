"""
Comprehensive logging configuration for SwarmBot
Provides structured logging with error tracking and dashboard integration
"""

import logging
import logging.handlers
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
            'logger_name': record.name
        }
        
        # Add error information if present
        if record.exc_info:
            log_data['error_type'] = record.exc_info[0].__name__
            log_data['error_message'] = str(record.exc_info[1])
            log_data['stack_trace'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """Console formatter with color support"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m'  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors for console output"""
        # Get color for level
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build the message
        message = f"{color}[{timestamp}] {record.levelname:<8}{self.RESET} "
        message += f"{record.name:<20} - {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


class ErrorTracker:
    """Tracks errors for dashboard display and analysis"""
    
    def __init__(self, max_errors: int = 1000):
        """Initialize error tracker with maximum error count"""
        self.max_errors = max_errors
        self.errors = []
        self.error_counts = {}
    
    def track_error(self, record: logging.LogRecord):
        """Track an error for analysis"""
        if record.levelno >= logging.ERROR:
            error_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'module': record.module,
                'function': record.funcName,
                'message': record.getMessage(),
                'error_type': None,
                'stack_trace': None
            }
            
            if record.exc_info:
                error_data['error_type'] = record.exc_info[0].__name__
                error_data['stack_trace'] = traceback.format_exception(*record.exc_info)
                
                # Track error counts by type
                error_type = error_data['error_type']
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            
            # Add to list with size limit
            self.errors.append(error_data)
            if len(self.errors) > self.max_errors:
                self.errors.pop(0)
    
    def get_recent_errors(self, count: int = 50) -> list:
        """Get recent errors"""
        return self.errors[-count:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        return {
            'total_errors': len(self.errors),
            'error_types': self.error_counts,
            'recent_errors': self.get_recent_errors(10)
        }


class SwarmBotLoggingHandler(logging.Handler):
    """Custom handler for SwarmBot-specific logging needs"""
    
    def __init__(self, error_tracker: Optional[ErrorTracker] = None):
        """Initialize with optional error tracker"""
        super().__init__()
        self.error_tracker = error_tracker
    
    def emit(self, record: logging.LogRecord):
        """Process log record"""
        if self.error_tracker:
            self.error_tracker.track_error(record)


# Global error tracker instance
error_tracker = ErrorTracker()


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Set up comprehensive logging for SwarmBot
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to files
        log_to_console: Whether to log to console
        log_dir: Directory for log files
    
    Returns:
        Configured root logger
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # File handlers
    if log_to_file:
        # JSON formatted file handler
        json_handler = logging.handlers.RotatingFileHandler(
            log_path / 'swarmbot.json',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        json_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(json_handler)
        
        # Error-only file handler
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / 'swarmbot_errors.log',
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(error_handler)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredConsoleFormatter())
        root_logger.addHandler(console_handler)
    
    # Add custom SwarmBot handler with error tracking
    swarmbot_handler = SwarmBotLoggingHandler(error_tracker)
    swarmbot_handler.setLevel(logging.ERROR)
    root_logger.addHandler(swarmbot_handler)
    
    # Log startup message
    root_logger.info(
        "SwarmBot logging initialized",
        extra={
            'log_level': log_level,
            'log_to_file': log_to_file,
            'log_to_console': log_to_console,
            'log_dir': str(log_path.absolute())
        }
    )
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_with_context(logger: logging.Logger, level: str, message: str, **context):
    """Log a message with additional context"""
    level_num = getattr(logging, level.upper())
    logger.log(level_num, message, extra=context)


def safe_log_error(logger: logging.Logger, message: str, exc_info=None, **context):
    """Safely log an error with exception information"""
    try:
        if exc_info is True:
            exc_info = sys.exc_info()
        logger.error(message, exc_info=exc_info, extra=context)
    except Exception as e:
        # Fallback if logging fails
        print(f"Logging error: {e}")
        print(f"Original message: {message}")


# Decorators for automatic error logging
def log_errors(logger_name: Optional[str] = None):
    """Decorator to automatically log errors from a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}",
                    exc_info=True,
                    extra={
                        'function': func.__name__,
                        'module': func.__module__,
                        'args': str(args)[:200],  # Limit size
                        'kwargs': str(kwargs)[:200]
                    }
                )
                raise
        return wrapper
    return decorator


def log_async_errors(logger_name: Optional[str] = None):
    """Decorator for async functions to automatically log errors"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in async {func.__name__}",
                    exc_info=True,
                    extra={
                        'function': func.__name__,
                        'module': func.__module__,
                        'args': str(args)[:200],
                        'kwargs': str(kwargs)[:200]
                    }
                )
                raise
        return wrapper
    return decorator


# Example usage patterns
class LoggingMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        return self._logger
    
    def log_debug(self, message: str, **context):
        """Log debug message with context"""
        self.logger.debug(message, extra=context)
    
    def log_info(self, message: str, **context):
        """Log info message with context"""
        self.logger.info(message, extra=context)
    
    def log_warning(self, message: str, **context):
        """Log warning message with context"""
        self.logger.warning(message, extra=context)
    
    def log_error(self, message: str, exc_info=None, **context):
        """Log error message with context"""
        self.logger.error(message, exc_info=exc_info, extra=context)
    
    def log_critical(self, message: str, exc_info=None, **context):
        """Log critical message with context"""
        self.logger.critical(message, exc_info=exc_info, extra=context)


if __name__ == "__main__":
    # Test logging setup
    setup_logging(log_level="DEBUG")
    
    # Test different log levels
    logger = get_logger("test")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception:
        logger.error("Error occurred", exc_info=True)
    
    # Test structured logging
    log_with_context(
        logger, "INFO", "User action",
        user_id="123", action="login", ip_address="192.168.1.1"
    )
    
    # Show error summary
    print("\nError Summary:")
    print(json.dumps(error_tracker.get_error_summary(), indent=2))
