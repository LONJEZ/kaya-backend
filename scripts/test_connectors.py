"""Test connector functionality"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8007"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo Electronics"})


def test_register_sheets_connector():
    """Test registering Google Sheets connector"""
    token = get_demo_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    config = {
        "source_id": "sales-sheet-2025",
        "type": "sheets",
        "spreadsheet_id": "1abc123def456",  # Replace with real ID
        "sheet_name": "Transactions",
        "credentials_path": "/path/to/credentials.json"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/connectors/register",
        headers=headers,
        json=config
    )
    
    print("📝 Register Sheets Connector")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_sync_connector():
    """Test triggering sync"""
    token = get_demo_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    sync_request = {
        "source_id": "sales-sheet-2025",
        "force_full_sync": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/connectors/sync",
        headers=headers,
        json=sync_request
    )
    
    print("🔄 Trigger Sync")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_connector_status():
    """Test getting connector status"""
    token = get_demo_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(
        f"{BASE_URL}/api/connectors/status/sales-sheet-2025",
        headers=headers
    )
    
    print("📊 Connector Status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_csv_with_idempotency():
    """Test CSV upload with duplicate detection"""
    token = get_demo_token()
    
    # Create CSV with duplicate entries
    sample_csv = """Date,Item,Amount,Category,Payment Method
2025-10-01,iPhone 15,120000,Electronics,M-Pesa
2025-10-02,Laptop Case,2500,Accessories,Cash
2025-10-01,iPhone 15,120000,Electronics,M-Pesa
2025-10-03,Headphones,4500,Electronics,Card"""
    
    csv_path = Path("/tmp/test_duplicates.csv")
    csv_path.write_text(sample_csv)
    
    # Upload first time
    with open(csv_path, 'rb') as f:
        files = {'file': ('transactions.csv', f, 'text/csv')}
        headers = {'Authorization': f'Bearer {token}'}
        
        response1 = requests.post(
            f"{BASE_URL}/api/ingestion/upload/csv?source_type=sheets",
            files=files,
            headers=headers
        )
    
    print("📤 First Upload (with duplicates)")
    print(f"Status: {response1.status_code}")
    result1 = response1.json()
    print(f"Rows uploaded: {result1.get('rows_uploaded')}")
    print()
    
    # Upload again (should skip duplicates)
    with open(csv_path, 'rb') as f:
        files = {'file': ('transactions.csv', f, 'text/csv')}
        
        response2 = requests.post(
            f"{BASE_URL}/api/ingestion/upload/csv?source_type=sheets",
            files=files,
            headers=headers
        )
    
    print("📤 Second Upload (should detect duplicates)")
    print(f"Status: {response2.status_code}")
    result2 = response2.json()
    print(f"Rows uploaded: {result2.get('rows_uploaded')}")
    print()


if __name__ == "__main__":
    print("="*60)
    print("🧪 Kaya AI Connector Tests")
    print("="*60)
    print()
    
    # Test CSV with idempotency
    test_csv_with_idempotency()
    
    # Note: Sheets tests require valid Google credentials
    print("📝 Note: Sheets connector tests require valid Google credentials")
    print("   Set up credentials and update test_register_sheets_connector()")

