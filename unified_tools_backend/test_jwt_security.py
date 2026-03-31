import requests
import json

def test_jwt_authentication():
    """Test JWT authentication and security validation"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing JWT Authentication and Security Implementation")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health_data = response.json()
        print(f"✅ Health check: {health_data['status']}")
        print(f"   JWT enabled: {health_data['security']['jwt_enabled']}")
        print(f"   Token expiry: {health_data['security']['token_expiry_minutes']} minutes")
        print(f"   Demo users: {health_data['security']['demo_users']}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Authentication
    print("\n2️⃣ Testing authentication...")
    auth_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/login", json=auth_data, timeout=5)
        auth_result = response.json()
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
            print(f"   Token type: {auth_result['token_type']}")
            print(f"   Expires in: {auth_result['expires_in']} seconds")
            access_token = auth_result['access_token']
        else:
            print(f"❌ Authentication failed: {auth_result}")
            return
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test 3: Token validation
    print("\n3️⃣ Testing token validation...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Test protected endpoint
        test_data = {"url": "http://info.cern.ch"}
        response = requests.post(f"{base_url}/api/scrape", json=test_data, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            print("✅ Token validation successful!")
            result = response.json()
            print(f"   Response contains: {list(result.keys())}")
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Token validation error: {e}")
        return
    
    # Test 4: Security headers
    print("\n4️⃣ Testing security headers...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        headers = response.headers
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Referrer-Policy',
            'Content-Security-Policy'
        ]
        
        found_headers = []
        for header in security_headers:
            if header in headers:
                found_headers.append(header)
                print(f"✅ {header}: {headers[header]}")
        
        print(f"\n   Security headers implemented: {len(found_headers)}/{len(security_headers)}")
        
    except Exception as e:
        print(f"❌ Security headers test failed: {e}")
    
    # Test 5: Invalid token handling
    print("\n5️⃣ Testing invalid token handling...")
    try:
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        response = requests.post(f"{base_url}/api/scrape", json=test_data, headers=invalid_headers, timeout=5)
        
        if response.status_code == 401:
            print("✅ Invalid token properly rejected!")
        else:
            print(f"❌ Invalid token test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid token test error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ JWT Authentication and Security Validation Complete!")
    return

if __name__ == "__main__":
    test_jwt_authentication()