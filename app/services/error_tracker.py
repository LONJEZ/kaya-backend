"""Error tracking and reporting"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class ErrorTracker:
    """Track and report application errors"""
    
    def __init__(self):
        self.errors = []
        self.error_counts = defaultdict(int)
    
    def track_error(
        self,
        error_type: str,
        error_message: str,
        endpoint: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Track an error"""
        error_record = {
            "type": error_type,
            "message": error_message,
            "endpoint": endpoint,
            "user_id": user_id,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.errors.append(error_record)
        self.error_counts[error_type] += 1
        
        # Log error
        logger.error(
            f"Error tracked: {error_type} - {error_message}",
            extra=error_record
        )
        
        # Keep only last 1000 errors
        if len(self.errors) > 1000:
            self.errors = self.errors[-1000:]
    
    def get_recent_errors(self, limit: int = 50) -> list:
        """Get recent errors"""
        return self.errors[-limit:]
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get error counts by type"""
        return dict(self.error_counts)


error_tracker = ErrorTracker()

