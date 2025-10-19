"""Advanced observability with structured logging"""

import logging
import json
from datetime import datetime
from typing import Optional
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class StructuredLogger:
    """Structured JSON logging for production"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter for production
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def log(self, level: str, message: str, **kwargs):
        """Log with structured data"""
        extra = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': request_id_var.get(),
            'user_id': user_id_var.get(),
            **kwargs
        }
        
        getattr(self.logger, level)(message, extra={'structured': extra})
    
    def info(self, message: str, **kwargs):
        self.log('info', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log('error', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log('warning', message, **kwargs)


class JSONFormatter(logging.Formatter):
    """Format logs as JSON"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        }
        
        # Add structured data if present
        if hasattr(record, 'structured'):
            log_data.update(record.structured)
        
        return json.dumps(log_data)
