"""
Cleanup script to remove old ingestion-specific tables
(mpesa, pos, sheets) from BigQuery.
"""

from app.utils.bigquery_client import bq_client
from google.cloud.exceptions import NotFound
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_tables():
    # List of old redundant tables to delete
    tables_to_delete = ["mpesa", "pos", "sheets"]

    for table_name in tables_to_delete:
        table_id = f"{bq_client.dataset_id}.{table_name}"

        try:
            bq_client.client.delete_table(table_id, not_found_ok=True)
            logger.info(f"✅ Deleted table {table_id}")
        except NotFound:
            logger.info(f"⚠️ Table {table_id} not found (already removed)")


if __name__ == "__main__":
    logger.info("🚀 Starting BigQuery cleanup...")
    cleanup_tables()
    logger.info("🎉 Cleanup complete!")
