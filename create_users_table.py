"""Create users table in BigQuery"""
from google.cloud import bigquery
from app.config import settings

def create_users_table():
    """Create the users table with correct schema"""
    client = bigquery.Client(project=settings.GCP_PROJECT_ID)
    
    table_id = f"{settings.GCP_PROJECT_ID}.{settings.BIGQUERY_DATASET}.users"
    
    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED", description="Unique user ID"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED", description="User email"),
        bigquery.SchemaField("password_hash", "STRING", mode="REQUIRED", description="Hashed password"),
        bigquery.SchemaField("business_name", "STRING", mode="REQUIRED", description="Business name"),
        bigquery.SchemaField("full_name", "STRING", mode="REQUIRED", description="Full name"),
        bigquery.SchemaField("currency", "STRING", mode="NULLABLE", description="Preferred currency"),
        bigquery.SchemaField("language", "STRING", mode="NULLABLE", description="Preferred language"),
        bigquery.SchemaField("refresh_frequency", "STRING", mode="NULLABLE", description="Data refresh frequency"),
        bigquery.SchemaField("settings", "JSON", mode="NULLABLE", description="User settings"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Creation timestamp"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE", description="Last update timestamp"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    
    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✅ Table {table_id} created successfully!")
        print(f"   Columns: {', '.join([field.name for field in schema])}")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    create_users_table()
