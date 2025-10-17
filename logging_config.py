"""
Logging Configuration for GDP Analytics Application
================================================

This module provides centralized logging configuration for the entire application.
It creates structured logs that help with debugging and monitoring.
"""

import logging
import logging.handlers
import os
import time
from datetime import datetime
import sys

def setup_logging(app=None, log_level='INFO'):
    """
    Set up comprehensive logging for the GDP Analytics application.
    
    Args:
        app: Flask application instance (optional)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Define log file paths
    main_log_file = os.path.join(logs_dir, 'gdp_analytics.log')
    error_log_file = os.path.join(logs_dir, 'gdp_analytics_errors.log')
    access_log_file = os.path.join(logs_dir, 'gdp_analytics_access.log')
    
    # Configure log formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | Line:%(lineno)-3d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console Handler (for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Main Log File Handler (all logs)
    main_file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    main_file_handler.setLevel(logging.DEBUG)
    main_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(main_file_handler)
    
    # Error Log File Handler (errors and warnings only)
    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,   # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_file_handler)
    
    # Configure specific loggers
    
    # Flask application logger
    if app:
        app.logger.setLevel(logging.INFO)
        
        # Access log handler for Flask requests
        access_handler = logging.handlers.RotatingFileHandler(
            access_log_file,
            maxBytes=5*1024*1024,   # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(detailed_formatter)  # Use the standard detailed formatter
        
        # Custom request logger
        request_logger = logging.getLogger('gdp_analytics.requests')
        request_logger.addHandler(access_handler)
        request_logger.addHandler(access_handler)
        request_logger.setLevel(logging.INFO)
    
    # Database operations logger
    db_logger = logging.getLogger('gdp_analytics.database')
    db_logger.setLevel(logging.DEBUG)
    
    # Data processing logger
    processing_logger = logging.getLogger('gdp_analytics.processing')
    processing_logger.setLevel(logging.DEBUG)
    
    # Chart generation logger
    chart_logger = logging.getLogger('gdp_analytics.charts')
    chart_logger.setLevel(logging.DEBUG)
    
    # ML models logger
    ml_logger = logging.getLogger('gdp_analytics.ml')
    ml_logger.setLevel(logging.DEBUG)
    
    # Suppress verbose third-party loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Log the setup completion
    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info("GDP Analytics Logging System Initialized")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"Main Log: {main_log_file}")
    logger.info(f"Error Log: {error_log_file}")
    logger.info(f"Access Log: {access_log_file}")
    logger.info("="*60)
    
    return {
        'main_log': main_log_file,
        'error_log': error_log_file,
        'access_log': access_log_file
    }

def get_logger(name):
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)

def log_function_call(func):
    """
    Decorator to log function calls and execution time.
    
    Usage:
        @log_function_call
        def my_function():
            pass
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            logger.debug(f"Function {func.__name__} completed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Function {func.__name__} failed after {execution_time:.2f}ms: {str(e)}")
            raise
    
    return wrapper

def log_database_operation(operation_type, table=None, query=None, params=None):
    """
    Log database operations for debugging.
    
    Args:
        operation_type: Type of operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name (optional)
        query: SQL query (optional)
        params: Query parameters (optional)
    """
    logger = get_logger('gdp_analytics.database')
    
    log_msg = f"DB Operation: {operation_type}"
    if table:
        log_msg += f" on table '{table}'"
    if query:
        log_msg += f" | Query: {query[:100]}{'...' if len(query) > 100 else ''}"
    if params:
        log_msg += f" | Params: {params}"
    
    logger.debug(log_msg)

def log_request(request, response, start_time):
    """
    Log HTTP request details.
    
    Args:
        request: Flask request object
        response: Flask response object
        start_time: Request start timestamp
    """
    logger = get_logger('gdp_analytics.requests')
    
    response_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"{request.remote_addr} | {request.method} | {request.url} | "
        f"{response.status_code} | {response_time:.2f}ms"
    )

# Exception logging utilities
def log_exception(e, context=""):
    """
    Log exceptions with full traceback.
    
    Args:
        e: Exception object
        context: Additional context information
    """
    logger = get_logger('gdp_analytics.errors')
    
    import traceback
    
    error_msg = f"Exception occurred: {str(e)}"
    if context:
        error_msg += f" | Context: {context}"
    
    logger.error(error_msg)
    logger.error(f"Traceback:\n{traceback.format_exc()}")

class LoggingMiddleware:
    """
    WSGI middleware for logging requests and responses.
    """
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger('gdp_analytics.middleware')
    
    def __call__(self, environ, start_response):
        import time
        start_time = time.time()
        
        def new_start_response(status, response_headers, exc_info=None):
            response_time = (time.time() - start_time) * 1000
            
            self.logger.info(
                f"{environ.get('REMOTE_ADDR', 'unknown')} | "
                f"{environ.get('REQUEST_METHOD', 'unknown')} | "
                f"{environ.get('PATH_INFO', 'unknown')} | "
                f"{status} | {response_time:.2f}ms"
            )
            
            return start_response(status, response_headers, exc_info)
        
        return self.app(environ, new_start_response)