"""
Load sample data into BigQuery for demo purposes
Run this after setting up tables to populate with realistic African SME data
"""

from datetime import datetime, timedelta
import random
import uuid
from google.cloud import bigquery

from app.config import settings
from app.utils.bigquery_client import bq_client

# Sample data constants
SAMPLE_USER_ID = "demo-user-001"
SAMPLE_BUSINESS = "Demo Electronics Kenya"

# Kenyan products common in SME retail
PRODUCTS = [
    {"name": "iPhone 15 Pro", "category": "Electronics", "price": 120000, "cost": 95000},
    {"name": "Samsung Galaxy A54", "category": "Electronics", "price": 45000, "cost": 38000},
    {"name": "HP Laptop", "category": "Electronics", "price": 65000, "cost": 52000},
    {"name": "JBL Bluetooth Speaker", "category": "Electronics", "price": 4500, "cost": 3200},
    {"name": "Sony Headphones", "category": "Electronics", "price": 8500, "cost": 6500},
    {"name": "USB-C Cable", "category": "Accessories", "price": 800, "cost": 400},
    {"name": "Phone Case", "category": "Accessories", "price": 1200, "cost": 600},
    {"name": "Screen Protector", "category": "Accessories", "price": 500, "cost": 250},
    {"name": "Power Bank 20000mAh", "category": "Accessories", "price": 3500, "cost": 2200},
    {"name": "Wireless Mouse", "category": "Accessories", "price": 1500, "cost": 900},
]

PAYMENT_METHODS = ["M-Pesa", "Cash", "Card", "Bank Transfer"]


def generate_sample_user():
    """Generate sample user data"""
    return {
        "id": SAMPLE_USER_ID,
        "email": "demo@kayaai.com",
        "business_name": SAMPLE_BUSINESS,
        "full_name": "Demo User",
        "currency": "KES",
        "language": "en",
        "refresh_frequency": "hourly",
        "settings": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


def generate_sample_products():
    """Generate sample products"""
    products = []
    for product in PRODUCTS:
        margin = ((product["price"] - product["cost"]) / product["price"]) * 100
        products.append({
            "id": str(uuid.uuid4()),
            "user_id": SAMPLE_USER_ID,
            "name": product["name"],
            "category": product["category"],
            "price": product["price"],
            "cost": product["cost"],
            "margin": round(margin, 2),
            "stock_quantity": random.randint(10, 100),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        })
    return products


def generate_sample_transactions(num_days=90, transactions_per_day_range=(5, 15)):
    """Generate realistic transaction history"""
    transactions = []
    end_date = datetime.utcnow()
    
    for day_offset in range(num_days):
        current_date = end_date - timedelta(days=day_offset)
        num_transactions = random.randint(*transactions_per_day_range)
        
        for _ in range(num_transactions):
            product = random.choice(PRODUCTS)
            quantity = random.randint(1, 3)
            amount = product["price"] * quantity
            
            # Random time during business hours (8am - 8pm)
            hour = random.randint(8, 20)
            minute = random.randint(0, 59)
            timestamp = current_date.replace(hour=hour, minute=minute, second=0)
            
            transactions.append({
                "id": str(uuid.uuid4()),
                "user_id": SAMPLE_USER_ID,
                "source": random.choice(["pos", "mpesa", "sheets"]),
                "amount": float(amount),
                "currency": "KES",
                "date": current_date.date().isoformat(),
                "timestamp": timestamp.isoformat(),
                "category": product["category"],
                "item_name": product["name"],
                "payment_method": random.choice(PAYMENT_METHODS),
                "status": "completed",
                "metadata": {
                    "quantity": quantity,
                    "unit_price": product["price"]
                },
                "created_at": timestamp.isoformat(),
            })
    
    return transactions


def load_sample_data():
    """Load all sample data into BigQuery"""
    print("🎯 Loading sample data into BigQuery...")
    
    try:
        # Load user
        print("👤 Loading user...")
        user = generate_sample_user()
        bq_client.insert_rows("users", [user])
        print(f"✅ Loaded user: {user['business_name']}")
        
        # Load products
        print("📦 Loading products...")
        products = generate_sample_products()
        bq_client.insert_rows("products", products)
        print(f"✅ Loaded {len(products)} products")
        
        # Load transactions (in batches of 500 to avoid payload limits)
        print("💰 Loading transactions...")
        transactions = generate_sample_transactions(num_days=90)
        
        batch_size = 500
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            bq_client.insert_rows("transactions", batch)
            print(f"   📊 Loaded batch {i//batch_size + 1}: {len(batch)} transactions")
        
        print(f"✅ Loaded {len(transactions)} total transactions")
        
        # Print summary
        print("\n" + "="*60)
        print("✨ Sample Data Summary")
        print("="*60)
        print(f"User: {user['business_name']}")
        print(f"User ID: {SAMPLE_USER_ID}")
        print(f"Products: {len(products)}")
        print(f"Transactions: {len(transactions)} (last 90 days)")
        print(f"Date Range: {transactions[-1]['date']} to {transactions[0]['date']}")
        
        # Calculate totals
        total_revenue = sum(t["amount"] for t in transactions)
        print(f"Total Revenue: KES {total_revenue:,.2f}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        raise
