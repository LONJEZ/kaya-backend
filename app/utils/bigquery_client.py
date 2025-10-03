from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
from typing import List, Dict, Any
import logging
import os

from app.config import settings
from app.models.bigquery import (
    TRANSACTIONS_SCHEMA,
    PRODUCTS_SCHEMA,
    USERS_SCHEMA,
    TRANSACTIONS_PARTITIONING
)

logger = logging.getLogger(__name__)


class BigQueryClient:
    """Wrapper for BigQuery operations"""
    
    def __init__(self):
        # Expand env vars like $HOME if present
        credentials_path = os.path.expandvars(settings.GOOGLE_APPLICATION_CREDENTIALS)

        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        
        self.client = bigquery.Client(
            project=settings.GCP_PROJECT_ID,
            credentials=credentials
        )
        self.dataset_id = f"{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}"
    
    def create_dataset(self):
        """Create dataset if it doesn't exist"""
        try:
            self.client.get_dataset(self.dataset_id)
            logger.info(f"Dataset {self.dataset_id} already exists")
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_id)
            dataset.location = "US"
            dataset = self.client.create_dataset(dataset, timeout=30)
            logger.info(f"Created dataset {self.dataset_id}")
    
    def create_tables(self):
        """Create all required tables with schemas"""
        tables = [
            ("transactions", TRANSACTIONS_SCHEMA, TRANSACTIONS_PARTITIONING),
            ("products", PRODUCTS_SCHEMA, None),
            ("users", USERS_SCHEMA, None),
        ]
        
        for table_name, schema, partitioning in tables:
            table_id = f"{self.dataset_id}.{table_name}"
            
            try:
                self.client.get_table(table_id)
                logger.info(f"Table {table_id} already exists")
            except NotFound:
                table = bigquery.Table(table_id, schema=schema)
                
                # Add partitioning for transactions
                if partitioning:
                    table.time_partitioning = bigquery.TimePartitioning(
                        type_=bigquery.TimePartitioningType.DAY,
                        field="date"
                    )
                
                table = self.client.create_table(table)
                logger.info(f"Created table {table_id}")
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dicts"""
        query_job = self.client.query(query)
        results = query_job.result()
        return [dict(row) for row in results]
    
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """Insert rows into a table"""
        table_id = f"{self.dataset_id}.{table_name}"
        errors = self.client.insert_rows_json(table_id, rows)
        
        if errors:
            logger.error(f"Errors inserting rows: {errors}")
            raise Exception(f"Failed to insert rows: {errors}")
        
        logger.info(f"Inserted {len(rows)} rows into {table_name}")


# Initialize client
bq_client = BigQueryClient()
