"""Test all advanced analytics endpoints"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8007"


def get_demo_token():
    """Generate demo token"""
    from app.auth import create_access_token
    return create_access_token({
        "sub": "demo-user-001",
        "business_name": "Demo Electronics"
    })


def test_endpoint(name: str, endpoint: str, token: str) -> Dict[str, Any]:
    """Test an endpoint"""
    print(f"\n{'='*70}")
    print(f"📊 {name}")
    print(f"{'='*70}")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, default=str))
            return {"passed": True, "data": data}
        else:
            print(f"Error: {response.text}")
            return {"passed": False, "error": response.text}
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"passed": False, "error": str(e)}


def main():
    print("🧪 Testing Advanced Analytics Endpoints")
    print("="*70)
    
    token = get_demo_token()
    print(f"✅ Token generated")
    
    endpoints = [
        ("Growth Metrics (MoM/YoY)", "/api/analytics/advanced/growth-metrics"),
        ("Customer Insights", "/api/analytics/advanced/customer-insights"),
        ("Profit Analysis", "/api/analytics/advanced/profit-analysis"),
        ("Cohort Analysis", "/api/analytics/advanced/cohort-analysis?period=month"),
        ("Revenue Forecast", "/api/analytics/advanced/revenue-forecast?months=3"),
        ("Product Performance", "/api/analytics/advanced/product-performance?limit=10"),
        ("Seasonal Analysis", "/api/analytics/advanced/seasonal-analysis"),
        ("Customer Segments", "/api/analytics/advanced/customer-segments"),
        ("Inventory Velocity", "/api/analytics/advanced/inventory-velocity?limit=5"),
    ]
    
    results = []
    for name, endpoint in endpoints:
        result = test_endpoint(name, endpoint, token)
        results.append({"name": name, "passed": result["passed"]})
    
    # Summary
    print(f"\n{'='*70}")
    print("📋 Test Summary")
    print(f"{'='*70}")
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    for result in results:
        status = "✅" if result["passed"] else "❌"
        print(f"{status} {result['name']}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All advanced analytics endpoints working!")
    else:
        print("⚠️  Some endpoints need attention")
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()