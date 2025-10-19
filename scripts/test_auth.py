"""Test authentication endpoints"""

import requests
import json

BASE_URL = "http://localhost:8007"


def test_registration():
    """Test user registration"""
    print("\n🧪 Testing Registration")
    print("=" * 60)
    
    data = {
        "email": "test@kayaai.com",
        "password": "testpass123",
        "business_name": "Test Business Ltd",
        "full_name": "Test User",
        "currency": "KES",
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Registration successful")
        print(f"Token: {result['access_token'][:50]}...")
        print(f"User: {result['user']['email']}")
        return result['access_token']
    else:
        print(f"❌ Registration failed: {response.text}")
        return None


def test_login(email: str, password: str):
    """Test user login"""
    print("\n🧪 Testing Login")
    print("=" * 60)
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Login successful")
        print(f"Token: {result['access_token'][:50]}...")
        print(f"User: {result['user']['email']}")
        return result['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def test_get_user(token: str):
    """Test get current user"""
    print("\n🧪 Testing Get Current User")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        user = response.json()
        print("✅ User info retrieved")
        print(json.dumps(user, indent=2))
    else:
        print(f"❌ Failed: {response.text}")


def test_refresh_token(token: str):
    """Test token refresh"""
    print("\n🧪 Testing Token Refresh")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/auth/refresh", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Token refreshed")
        print(f"New Token: {result['access_token'][:50]}...")
        return result['access_token']
    else:
        print(f"❌ Failed: {response.text}")
        return None


def main():
    print("🔐 Kaya AI Authentication Tests")
    print("=" * 60)
    
    # Test 1: Register
    token = test_registration()
    
    if not token:
        print("\n⚠️  Registration failed, trying login with existing account...")
        token = test_login("test@kayaai.com", "testpass123")
    
    if token:
        # Test 2: Get user info
        test_get_user(token)
        
        # Test 3: Refresh token
        new_token = test_refresh_token(token)
        
        # Test 4: Login again
        test_login("test@kayaai.com", "testpass123")
    
    print("\n" + "=" * 60)
    print("✅ Authentication tests complete")
    print("=" * 60)


if __name__ == "__main__":
    main()