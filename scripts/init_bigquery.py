"""
Initialize BigQuery dataset and tables
Run this once during setup
"""

from app.utils.bigquery_client import bq_client


def init_bigquery():
    """Initialize BigQuery dataset and tables"""
    print("🗄️  Initializing BigQuery...")
    
    try:
        # Create dataset
        print("📁 Creating dataset...")
        bq_client.create_dataset()
        
        # Create tables
        print("📋 Creating tables...")
        bq_client.create_tables()
        
        print("\n✅ BigQuery initialization complete!")
        print(f"Dataset: {bq_client.dataset_id}")
        print("Tables: transactions, products, users")
        
    except Exception as e:
        print(f"❌ Error initializing BigQuery: {e}")
        raise


if __name__ == "__main__":
    init_bigquery()

