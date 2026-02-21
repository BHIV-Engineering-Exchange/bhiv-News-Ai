#!/usr/bin/env python3
"""
Contract Validation Test Script
Tests backend endpoints against orchestration_contract_v1.json specifications
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, get_db
from database import DatabaseManager
from fastapi.testclient import TestClient
import pytest

# Create test client
client = TestClient(app)

def get_auth_token():
    """Get authentication token for testing"""
    try:
        response = client.post("/token", data={"username": "testuser", "password": "testpass123"})
        if response.status_code == 200:
            return response.json()["access_token"]
    except:
        pass
    
    # Try to create user first
    try:
        client.post("/register", json={"username": "testuser", "password": "testpass123", "email": "test@example.com"})
        response = client.post("/token", data={"username": "testuser", "password": "testpass123"})
        if response.status_code == 200:
            return response.json()["access_token"]
    except:
        pass
    
    # Return a dummy token if auth fails
    return "dummy_token_for_testing"

def test_health_endpoint():
    """Test /health endpoint against contract"""
    print("=== HEALTH ENDPOINT TEST ===")
    
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        
        # Check contract requirements
        contract_keys = ["status", "timestamp", "services"]
        missing_keys = [key for key in contract_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Missing contract keys: {missing_keys}")
        else:
            print("✅ All contract keys present")
            
        # Check data types
        if "status" in data and isinstance(data["status"], str):
            print("✅ Status field correct type")
        else:
            print("❌ Status field incorrect type")
    else:
        print(f"❌ Health endpoint failed: {response.text}")

def test_scrape_endpoint():
    """Test /api/scrape endpoint against contract"""
    print("\n=== SCRAPE ENDPOINT TEST ===")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/scrape", 
        json={"url": "https://www.bbc.com/news", "max_pages": 1}, 
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        # Check contract requirements
        contract_keys = ["success", "data"]
        missing_keys = [key for key in contract_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Missing contract keys: {missing_keys}")
        else:
            print("✅ All contract keys present")
            
        # Check data types
        if "success" in data and isinstance(data["success"], bool):
            print("✅ Success field correct type")
        else:
            print("❌ Success field incorrect type")
            
        if "data" in data:
            print(f"✅ Data field present (type: {type(data['data'])})")
        else:
            print("❌ Data field missing")
    else:
        print(f"❌ Scrape endpoint failed: {response.text[:100]}")

def test_news_analysis_endpoint():
    """Test /api/news-analysis endpoint against contract"""
    print("\n=== NEWS ANALYSIS ENDPOINT TEST ===")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/news-analysis", 
        json={"url": "https://www.bbc.com/news", "analysis_type": "comprehensive"}, 
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        # Check contract requirements
        contract_keys = ["success", "analysis"]
        missing_keys = [key for key in contract_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Missing contract keys: {missing_keys}")
        else:
            print("✅ All contract keys present")
            
        # Check data types
        if "success" in data and isinstance(data["success"], bool):
            print("✅ Success field correct type")
        else:
            print("❌ Success field incorrect type")
            
        if "analysis" in data:
            print(f"✅ Analysis field present (type: {type(data['analysis'])})")
        else:
            print("❌ Analysis field missing")
    else:
        print(f"❌ News analysis endpoint failed: {response.text[:100]}")

def test_summarize_endpoint():
    """Test /api/summarize endpoint against contract"""
    print("\n=== SUMMARIZE ENDPOINT TEST ===")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    test_content = "This is a test article about current events and news analysis."
    
    response = client.post("/api/summarize", 
        json={"content": test_content, "max_length": 100}, 
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        # Check contract requirements
        contract_keys = ["success", "summary"]
        missing_keys = [key for key in contract_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Missing contract keys: {missing_keys}")
        else:
            print("✅ All contract keys present")
            
        # Check data types
        if "success" in data and isinstance(data["success"], bool):
            print("✅ Success field correct type")
        else:
            print("❌ Success field incorrect type")
            
        if "summary" in data and isinstance(data["summary"], str):
            print("✅ Summary field correct type")
        else:
            print("❌ Summary field incorrect type")
    else:
        print(f"❌ Summarize endpoint failed: {response.text[:100]}")

def test_scraped_news_endpoint():
    """Test /api/scraped-news endpoint against contract"""
    print("\n=== SCRAPED NEWS ENDPOINT TEST ===")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET
    response = client.get("/api/scraped-news", headers=headers)
    print(f"GET Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        # Check contract requirements
        contract_keys = ["success", "data", "count"]
        missing_keys = [key for key in contract_keys if key not in data]
        
        if missing_keys:
            print(f"❌ Missing contract keys: {missing_keys}")
        else:
            print("✅ All contract keys present")
            
        # Check data types
        if "success" in data and isinstance(data["success"], bool):
            print("✅ Success field correct type")
        else:
            print("❌ Success field incorrect type")
            
        if "data" in data and isinstance(data["data"], list):
            print(f"✅ Data field correct type (length: {len(data['data'])})")
        else:
            print("❌ Data field incorrect type")
            
        if "count" in data and isinstance(data["count"], int):
            print("✅ Count field correct type")
        else:
            print("❌ Count field incorrect type")
    else:
        print(f"❌ Scraped news GET failed: {response.text[:100]}")

if __name__ == "__main__":
    print("Contract Validation Test Suite")
    print("=" * 50)
    
    test_health_endpoint()
    test_scrape_endpoint()
    test_news_analysis_endpoint()
    test_summarize_endpoint()
    test_scraped_news_endpoint()
    
    print("\n" + "=" * 50)
    print("Contract validation complete")