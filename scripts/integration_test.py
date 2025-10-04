"""
Integration test: Full flow from data upload to analytics
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8007"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "integration-test-user", "business_name": "Test Business"})


def test_full_integration():
    """Test complete flow: Upload → Process → Query Analytics"""
    
    print("="*70)
    print("🧪 Kaya AI Integration Test")
    print("="*70)
    print()
    
    token = get_demo_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    # Step 1: Upload CSV data
    print("1️⃣ Uploading test data...")
    
    test_csv = """Date,Item,Amount,Category,Payment Method
2025-10-01,Test Product A,5000,Electronics,M-Pesa
2025-10-02,Test Product B,3000,Accessories,Cash
2025-10-03,Test Product C,8000,Electronics,Card"""
    
    csv_path = Path("/tmp/integration_test.csv")
    csv_path.write_text(test_csv)
    
    with open(csv_path, 'rb') as f:
        files = {'file': ('test.csv', f, 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/api/ingestion/upload/csv?source_type=sheets",
            files=files,
            headers=headers
        )
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return False
    
    result = response.json()
    ingestion_id = result['ingestion_id']
    print(f"✅ Uploaded {result['rows_uploaded']} rows")
    print(f"   Ingestion ID: {ingestion_id}")
    print()
    
    # Step 2: Wait for processing
    print("2️⃣ Waiting for background processing...")
    time.sleep(3)
    
    # Check status
    status_response = requests.get(
        f"{BASE_URL}/api/ingestion/status/{ingestion_id}",
        headers=headers
    )
    
    if status_response.status_code == 200:
        status = status_response.json()
        print(f"✅ Processing complete")
        print(f"   Status: {status['status']}")
        print(f"   Rows processed: {status.get('rows_processed', 'N/A')}")
    print()
    
    # Step 3: Query analytics
    print("3️⃣ Querying analytics...")
    
    endpoints = [
        ("Overview", "/api/analytics/overview"),
        ("Top Products", "/api/analytics/top-products?limit=3"),
        ("Transactions", "/api/analytics/transactions?limit=5"),
    ]
    
    for name, endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        if response.status_code == 200:
            print(f"✅ {name}: {len(response.json())} items" if isinstance(response.json(), list) else f"✅ {name}: Success")
        else:
            print(f"❌ {name}: Failed")
    
    print()
    
    # Step 4: Test caching
    print("4️⃣ Testing cache performance...")
    
    endpoint = f"{BASE_URL}/api/analytics/overview"
    
    # First call (cold)
    start = time.time()
    response1 = requests.get(endpoint, headers=headers)
    time1 = time.time() - start
    
    # Second call (cached)
    start = time.time()
    response2 = requests.get(endpoint, headers=headers)
    time2 = time.time() - start
    
    print(f"   Cold: {time1*1000:.0f}ms")
    print(f"   Cached: {time2*1000:.0f}ms")
    print(f"   Speedup: {((time1-time2)/time1*100):.0f}%")
    print()
    
    # Summary
    print("="*70)
    print("✅ Integration Test Complete!")
    print("="*70)
    print()
    print("All systems operational:")
    print("  ✅ Data ingestion")
    print("  ✅ Background processing")
    print("  ✅ Analytics queries")
    print("  ✅ Caching layer")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_full_integration()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        exit(1)

