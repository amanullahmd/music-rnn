"""
Logging configuration for Music Generation GUI
"""
import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Determine if running in production or development
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'

# Log file paths
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
GENERAL_LOG = os.path.join(LOGS_DIR, 'app.log')
ERROR_LOG = os.path.join(LOGS_DIR, 'errors.log')
REQUEST_LOG = os.path.join(LOGS_DIR, 'requests.log')


def setup_logging():
    """Configure logging for the application"""
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if not DEBUG_MODE else logging.DEBUG)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # General log file handler
    general_handler = logging.handlers.RotatingFileHandler(
        GENERAL_LOG,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    general_handler.setLevel(getattr(logging, LOG_LEVEL))
    general_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(general_handler)
    
    # Error log file handler
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Request log file handler
    request_logger = logging.getLogger('requests')
    request_handler = logging.handlers.RotatingFileHandler(
        REQUEST_LOG,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    request_handler.setLevel(logging.INFO)
    request_handler.setFormatter(detailed_formatter)
    request_logger.addHandler(request_handler)
    request_logger.propagate = False
    
    return root_logger


def get_request_logger():
    """Get the request logger"""
    return logging.getLogger('requests')


def log_request(method, path, status_code, duration_ms):
    """Log an HTTP request"""
    logger = get_request_logger()
    logger.info(f'{method} {path} - {status_code} ({duration_ms}ms)')


def log_error(error_type, error_message, stack_trace=None):
    """Log an error with context"""
    logger = logging.getLogger()
    logger.error(f'{error_type}: {error_message}')
    if stack_trace:
        logger.error(f'Stack trace: {stack_trace}')
