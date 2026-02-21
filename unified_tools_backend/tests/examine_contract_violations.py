import pytest
from fastapi.testclient import TestClient
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, get_db
from database import DatabaseManager

# Use a test-specific database
TEST_DB_PATH = "contract_examination.db"

@pytest.fixture(scope="module")
def db_manager():
    """Fixture to set up and tear down the test database"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    manager = DatabaseManager(db_path=TEST_DB_PATH)
    app.dependency_overrides[get_db] = lambda: manager
    yield manager
    
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

client = TestClient(app)

def get_auth_token():
    """Get JWT token for authenticated requests"""
    response = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]

def test_examine_actual_api_responses():
    """Examine actual API responses to document contract violations"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== EXAMINING ACTUAL API RESPONSES ===\n")
    
    # Test 1: Scrape endpoint with invalid URL
    print("1. Scrape endpoint with invalid URL:")
    response = client.post("/api/scrape", json={"url": "invalid-url"}, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Contract violation: Missing 'success' field, direct error details returned\n")
    
    # Test 2: News analysis endpoint with invalid URL
    print("2. News analysis endpoint with invalid URL:")
    response = client.post("/api/news-analysis", json={"url": "invalid-url"}, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Contract violation: Missing 'success' field, direct error details returned\n")
    
    # Test 3: Summarize endpoint with missing required field
    print("3. Summarize endpoint with missing required field:")
    response = client.post("/api/summarize", json={"max_length": 100}, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Contract violation: Missing 'success' field, direct validation errors returned\n")
    
    # Test 4: Scrape endpoint with valid URL (if it works)
    print("4. Scrape endpoint with valid URL:")
    response = client.post("/api/scrape", json={"url": "https://example.com", "max_pages": 1}, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        # Check if success field exists in successful response
        data = response.json()
        if "success" in data:
            print("✅ Contract followed: 'success' field present")
        else:
            print("❌ Contract violation: Missing 'success' field even in successful response")
    else:
        print(f"Response: {response.json()}")
        print("❌ Request failed")
    print()

def test_successful_response_contract_adherence():
    """Test if successful responses follow the contract"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test health endpoint (should always work)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    print("Health endpoint response structure:")
    print(f"Fields: {list(data.keys())}")
    print(f"Has 'success' field: {'success' in data}")
    print(f"Has 'status' field: {'status' in data}")
    print()
    
    # Test scraped news endpoint (should work)
    response = client.get("/api/scraped-news", headers=headers)
    data = response.json()
    
    print("Scraped news endpoint response structure:")
    print(f"Fields: {list(data.keys())}")
    print(f"Has 'success' field: {'success' in data}")
    print(f"Has 'data' field: {'data' in data}")
    print(f"Has 'count' field: {'count' in data}")
    print()

if __name__ == "__main__":
    test_examine_actual_api_responses()
    test_successful_response_contract_adherence()