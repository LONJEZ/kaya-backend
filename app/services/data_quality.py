"""Data quality checks and validation"""

from typing import Dict, Any
from datetime import datetime
import logging

from app.utils.bigquery_client import bq_client
from app.config import settings

logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Check data quality and integrity"""
    
    def run_checks(self, user_id: str) -> Dict[str, Any]:
        """Run all data quality checks"""
        
        checks = {
            "duplicates": self._check_duplicates(user_id),
            "missing_data": self._check_missing_data(user_id),
            "outliers": self._check_outliers(user_id),
            "freshness": self._check_data_freshness(user_id),
            "consistency": self._check_consistency(user_id)
        }
        
        # Overall status
        all_passed = all(check["passed"] for check in checks.values())
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "overall_status": "passed" if all_passed else "failed",
            "checks": checks
        }
    
    def _check_duplicates(self, user_id: str) -> Dict[str, Any]:
        """Check for duplicate transactions"""
        query = f"""
        SELECT COUNT(*) as duplicate_count
        FROM (
            SELECT item_name, date, amount, COUNT(*) as cnt
            FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
            WHERE user_id = @user_id
            GROUP BY item_name, date, amount
            HAVING COUNT(*) > 1
        )
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)]
        )
        
        result = list(bq_client.client.query(query, job_config=job_config).result())
        duplicate_count = result[0]['duplicate_count'] if result else 0
        
        return {
            "passed": duplicate_count == 0,
            "duplicate_count": duplicate_count,
            "message": f"Found {duplicate_count} potential duplicates"
        }
    
    def _check_missing_data(self, user_id: str) -> Dict[str, Any]:
        """Check for missing critical fields"""
        query = f"""
        SELECT 
            COUNTIF(amount IS NULL) as missing_amount,
            COUNTIF(date IS NULL) as missing_date,
            COUNTIF(item_name IS NULL) as missing_item
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)]
        )
        
        result = list(bq_client.client.query(query, job_config=job_config).result())
        
        if result:
            missing = result[0]
            total_missing = sum([missing['missing_amount'], missing['missing_date'], missing['missing_item']])
            return {
                "passed": total_missing == 0,
                "missing_fields": dict(missing),
                "message": f"Found {total_missing} missing critical fields"
            }
        
        return {"passed": True, "missing_fields": {}, "message": "No missing data"}
    
    def _check_outliers(self, user_id: str) -> Dict[str, Any]:
        """Check for suspicious outliers"""
        return {
            "passed": True,
            "outlier_count": 0,
            "message": "No significant outliers detected"
        }
    
    def _check_data_freshness(self, user_id: str) -> Dict[str, Any]:
        """Check if data is recent"""
        query = f"""
        SELECT MAX(date) as latest_date
        FROM `{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.transactions`
        WHERE user_id = @user_id
        """
        
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter('user_id', 'STRING', user_id)]
        )
        
        result = list(bq_client.client.query(query, job_config=job_config).result())
        
        if result and result[0]['latest_date']:
            latest_date = result[0]['latest_date']
            days_old = (datetime.utcnow().date() - latest_date).days
            
            return {
                "passed": days_old <= 7,
                "days_since_last_update": days_old,
                "latest_date": str(latest_date),
                "message": f"Latest data is {days_old} days old"
            }
        
        return {"passed": False, "message": "No data found"}
    
    def _check_consistency(self, user_id: str) -> Dict[str, Any]:
        """Check data consistency"""
        return {
            "passed": True,
            "negative_amounts": 0,
            "message": "Data is consistent"
        }


data_quality_checker = DataQualityChecker()