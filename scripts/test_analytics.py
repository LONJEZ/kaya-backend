"""Test analytics endpoints with real data"""

import requests
import json

BASE_URL = "http://localhost:8007"


def get_demo_token():
    from app.auth import create_access_token
    return create_access_token({"sub": "demo-user-001", "business_name": "Demo Electronics"})


def test_endpoint(name: str, endpoint: str, token: str):
    """Test an analytics endpoint"""
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    
    print(f"\n{'='*60}")
    print(f"📊 {name}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")


def main():
    print("🧪 Testing Analytics Endpoints with Real Data")
    
    token = get_demo_token()
    
    endpoints = [
        ("Overview", "/api/analytics/overview"),
        ("Revenue Trends", "/api/analytics/revenue-trends"),
        ("Top Products", "/api/analytics/top-products"),
        ("Category Sales", "/api/analytics/category-sales"),
        ("Recent Transactions", "/api/analytics/transactions?limit=10"),
        ("Payment Methods", "/api/analytics/payment-methods"),
    ]
    
    for name, endpoint in endpoints:
        test_endpoint(name, endpoint, token)
    
    print(f"\n{'='*60}")
    print("✅ All analytics tests complete")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()