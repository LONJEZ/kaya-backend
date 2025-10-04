from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
from typing import List, Dict, Any, Optional
import logging
import os
import tempfile
import json

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
        """Create required tables with schemas"""
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

                if partitioning:
                    table.time_partitioning = bigquery.TimePartitioning(
                        type_=bigquery.TimePartitioningType.DAY,
                        field="date"
                    )

                table = self.client.create_table(table)
                logger.info(f"Created table {table_id}")

    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """Insert rows into a table (batch load instead of streaming insert)."""
        table_id = f"{self.dataset_id}.{table_name}"

        if not rows:
            logger.warning("No rows to insert.")
            return

        # Write rows to a temporary JSON file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmpfile:
            for row in rows:
                tmpfile.write(json.dumps(row) + "\n")
            tmpfile.flush()

            # Configure batch load
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            )

            # Open the file for reading and load into BigQuery
            with open(tmpfile.name, "rb") as source_file:
                job = self.client.load_table_from_file(
                    source_file,
                    table_id,
                    job_config=job_config
                )
                job.result()  # Wait for the job to complete

        logger.info(f"Inserted {len(rows)} rows into {table_name} (batch load)")

    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Run a SQL query and return results as list of dicts."""
        job_config = bigquery.QueryJobConfig()

        if params:
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter(name, "STRING", value)
                for name, value in params.items()
            ]

        logger.info(f"Running query: {sql}")
        query_job = self.client.query(sql, job_config=job_config)
        results = query_job.result()

        rows = [dict(row) for row in results]
        logger.info(f"Query returned {len(rows)} rows")
        return rows
    
    def query_with_params(self, query: str, params: List[tuple]) -> List[Dict[str, Any]]:
        """Execute parameterized query"""
        from google.cloud import bigquery
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(name, type_, value)
                for name, type_, value in params
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        return [dict(row) for row in results]




# Initialize client
bq_client = BigQueryClient()
