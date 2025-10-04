"""BigQuery query optimization utilities"""

from typing import Dict, Any, List
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Optimize BigQuery queries for cost and performance"""
    
    @staticmethod
    def build_partitioned_query(
        table: str,
        user_id: str,
        days: int,
        select_fields: List[str],
        where_conditions: List[str] = None,
        group_by: List[str] = None,
        order_by: str = None,
        limit: int = None
    ) -> str:
        """
        Build optimized query with partition pruning
        
        Automatically adds date filter for partition pruning
        """
        fields = ", ".join(select_fields)
        
        conditions = [
            f"user_id = '{user_id}'",
            f"date >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)",
            f"date <= CURRENT_DATE()"
        ]
        
        if where_conditions:
            conditions.extend(where_conditions)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        SELECT {fields}
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.{table}`
        WHERE {where_clause}
        """
        
        if group_by:
            query += f"\nGROUP BY {', '.join(group_by)}"
        
        if order_by:
            query += f"\nORDER BY {order_by}"
        
        if limit:
            query += f"\nLIMIT {limit}"
        
        logger.info(f"Optimized query built for table={table}, days={days}")
        return query
    
    @staticmethod
    def estimate_query_cost(query: str) -> Dict[str, Any]:
        """
        Estimate BigQuery query cost
        Returns bytes processed and estimated cost
        """
        # This is a simplified estimate
        # In production, use bq_client.client.query(query, dry_run=True)
        
        # Rough estimate: 100KB per day of data per user
        import re
        
        days_match = re.search(r'INTERVAL (\d+) DAY', query)
        days = int(days_match.group(1)) if days_match else 30
        
        estimated_bytes = days * 100 * 1024  # 100KB per day
        cost_per_tb = 5.0  # $5 per TB
        estimated_cost = (estimated_bytes / (1024**4)) * cost_per_tb
        
        return {
            "estimated_bytes": estimated_bytes,
            "estimated_cost_usd": round(estimated_cost, 6),
            "is_partitioned": "date >=" in query.lower()
        }
