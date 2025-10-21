from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
from typing import List, Dict, Any, Optional
import logging
import os
import tempfile
import json
import base64

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
        """Initialize BigQuery client with credentials from file or base64 env var"""
        # Get the credentials path
        credentials_path = os.path.expandvars(settings.GOOGLE_APPLICATION_CREDENTIALS)
        
        # Check if credentials file exists
        if not os.path.exists(credentials_path):
            logger.info(f"Credentials file not found at {credentials_path}")
            logger.info("Attempting to create from GCP_CREDENTIALS_BASE64 environment variable...")
            
            # Get base64 credentials from environment
            base64_creds = os.getenv('GCP_CREDENTIALS_BASE64')
            
            if not base64_creds:
                error_msg = (
                    f"Credentials file not found at {credentials_path} and "
                    "GCP_CREDENTIALS_BASE64 environment variable is not set. "
                    "Please provide credentials via file or environment variable."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            try:
                # Decode base64 credentials
                logger.info("Decoding base64 credentials...")
                credentials_json = base64.b64decode(base64_creds).decode('utf-8')
                
                # Create directory if needed
                creds_dir = os.path.dirname(credentials_path)
                if creds_dir and not os.path.exists(creds_dir):
                    os.makedirs(creds_dir, exist_ok=True)
                    logger.info(f"Created directory: {creds_dir}")
                
                # Write credentials to file
                with open(credentials_path, 'w') as f:
                    f.write(credentials_json)
                
                logger.info(f"✅ Successfully created credentials file at {credentials_path}")
                
                # Verify the file was created
                if os.path.exists(credentials_path):
                    file_size = os.path.getsize(credentials_path)
                    logger.info(f"✅ Credentials file size: {file_size} bytes")
                else:
                    raise FileNotFoundError(f"Failed to create credentials file at {credentials_path}")
                    
            except Exception as e:
                error_msg = f"Failed to decode and write GCP credentials: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            logger.info(f"Found existing credentials file at {credentials_path}")
        
        # Load credentials from file
        try:
            logger.info("Loading credentials from file...")
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            
            # Initialize BigQuery client
            self.client = bigquery.Client(
                project=settings.GCP_PROJECT_ID,
                credentials=credentials
            )
            self.dataset_id = f"{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}"
            
            logger.info(f"✅ BigQuery client initialized successfully")
            logger.info(f"✅ Project: {settings.GCP_PROJECT_ID}")
            logger.info(f"✅ Dataset: {self.dataset_id}")
            
        except Exception as e:
            error_msg = f"Failed to initialize BigQuery client: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

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
