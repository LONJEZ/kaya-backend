"""Application monitoring and metrics"""

from typing import Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and report application metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
    
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Record API request metrics"""
        self.metrics[f"request_{endpoint}"].append({
            "duration": duration,
            "status": status_code,
            "timestamp": datetime.utcnow()
        })
        self.counters[f"requests_{endpoint}"] += 1
        
        if status_code >= 400:
            self.counters[f"errors_{endpoint}"] += 1
    
    def record_chat_query(self, duration: float, confidence: float):
        """Record chat metrics"""
        self.metrics["chat_queries"].append({
            "duration": duration,
            "confidence": confidence,
            "timestamp": datetime.utcnow()
        })
        self.counters["total_chat_queries"] += 1
    
    def record_data_ingestion(self, rows: int, duration: float):
        """Record ingestion metrics"""
        self.metrics["ingestion"].append({
            "rows": rows,
            "duration": duration,
            "timestamp": datetime.utcnow()
        })
        self.counters["total_rows_ingested"] += rows
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Calculate hourly stats
        recent_requests = [
            m for metrics in self.metrics.values()
            for m in metrics
            if m.get("timestamp", now) > hour_ago
        ]
        
        return {
            "total_requests": sum(
                v for k, v in self.counters.items()
                if k.startswith("requests_")
            ),
            "total_errors": sum(
                v for k, v in self.counters.items()
                if k.startswith("errors_")
            ),
            "total_chat_queries": self.counters["total_chat_queries"],
            "total_rows_ingested": self.counters["total_rows_ingested"],
            "requests_last_hour": len(recent_requests),
            "avg_response_time_ms": (
                sum(m.get("duration", 0) for m in recent_requests) /
                len(recent_requests) * 1000
                if recent_requests else 0
            )
        }


metrics_collector = MetricsCollector()