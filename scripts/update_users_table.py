"""Update users table to include password_hash field"""

from app.utils.bigquery_client import bq_client
from app.config import settings


def update_users_table():
    """Add password_hash column to existing users table"""
    
    print("Updating users table schema...")
    
    try:
        # Check if table exists
        table_id = f"{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.users"
        
        # Try to add column (BigQuery allows adding columns)
        query = f"""
        ALTER TABLE `{table_id}`
        ADD COLUMN IF NOT EXISTS password_hash STRING
        """
        
        bq_client.client.query(query).result()
        print("✅ Users table updated successfully")
        
    except Exception as e:
        print(f"Note: {e}")
        print("If table doesn't exist, it will be created with correct schema on first use")


if __name__ == "__main__":
    update_users_table()
