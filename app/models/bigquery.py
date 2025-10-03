"""
BigQuery Table Schemas for Kaya AI

Tables:
- transactions: All financial transactions from various sources
- products: Product catalog with pricing and margins
- users: Business users and their settings
"""

TRANSACTIONS_SCHEMA = [
    {"name": "id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "user_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "source", "type": "STRING", "mode": "REQUIRED"},  # 'mpesa', 'pos', 'sheets'
    {"name": "amount", "type": "FLOAT64", "mode": "REQUIRED"},
    {"name": "currency", "type": "STRING", "mode": "REQUIRED"},
    {"name": "date", "type": "DATE", "mode": "REQUIRED"},
    {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "category", "type": "STRING", "mode": "NULLABLE"},
    {"name": "item_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "payment_method", "type": "STRING", "mode": "NULLABLE"},
    {"name": "status", "type": "STRING", "mode": "NULLABLE"},
    {"name": "metadata", "type": "JSON", "mode": "NULLABLE"},
    {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
]

PRODUCTS_SCHEMA = [
    {"name": "id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "user_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "name", "type": "STRING", "mode": "REQUIRED"},
    {"name": "category", "type": "STRING", "mode": "NULLABLE"},
    {"name": "price", "type": "FLOAT64", "mode": "REQUIRED"},
    {"name": "cost", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "margin", "type": "FLOAT64", "mode": "NULLABLE"},
    {"name": "stock_quantity", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "updated_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
]

USERS_SCHEMA = [
    {"name": "id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "email", "type": "STRING", "mode": "REQUIRED"},
    {"name": "business_name", "type": "STRING", "mode": "REQUIRED"},
    {"name": "full_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "currency", "type": "STRING", "mode": "REQUIRED"},
    {"name": "language", "type": "STRING", "mode": "REQUIRED"},
    {"name": "refresh_frequency", "type": "STRING", "mode": "REQUIRED"},
    {"name": "settings", "type": "JSON", "mode": "NULLABLE"},
    {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "updated_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
]

# Partitioning configuration
TRANSACTIONS_PARTITIONING = {
    "type": "DAY",
    "field": "date"
}
