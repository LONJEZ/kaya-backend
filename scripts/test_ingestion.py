"""Test data ingestion endpoints"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8007"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo Electronics"})


def test_csv_upload():
    """Test CSV upload"""
    token = get_demo_token()
    
    # Create sample CSV
    sample_csv = """Date,Item,Amount,Category,Payment Method
2025-10-01,iPhone 15,120000,Electronics,M-Pesa
2025-10-02,Laptop Case,2500,Accessories,Cash
2025-10-03,Headphones,4500,Electronics,Card"""
    
    # Write to temp file
    csv_path = Path("/tmp/sample_transactions.csv")
    csv_path.write_text(sample_csv)
    
    # Upload
    with open(csv_path, 'rb') as f:
        files = {'file': ('transactions.csv', f, 'text/csv')}
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(
            f"{BASE_URL}/api/ingestion/upload/csv?source_type=sheets",
            files=files,
            headers=headers
        )
    
    print(f"Upload Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json().get('ingestion_id')


def test_ingestion_status(ingestion_id):
    """Check ingestion status"""
    token = get_demo_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(
        f"{BASE_URL}/api/ingestion/status/{ingestion_id}",
        headers=headers
    )
    
    print(f"\nStatus Check: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("🧪 Testing Data Ingestion")
    print("=" * 60)
    
    ingestion_id = test_csv_upload()
    
    if ingestion_id:
        import time
        time.sleep(2)  # Wait for background processing
        test_ingestion_status(ingestion_id)
