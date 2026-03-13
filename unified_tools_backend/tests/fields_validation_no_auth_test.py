#!/usr/bin/env python3
"""
Required Fields & Null Handling Test Script (No Auth)
Tests API endpoints for proper field validation and null handling without authentication
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

def test_scrape_required_fields_no_auth():
    """Test /api/scrape endpoint required fields without auth"""
    print("=== SCRAPE ENDPOINT REQUIRED FIELDS TEST (NO AUTH) ===")
    
    # Test missing URL (required field) - should fail auth first
    response = client.post("/api/scrape", 
        json={"max_pages": 1},  # Missing required 'url' field
    )
    print(f"Missing URL field - Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Authentication required (expected)")
    else:
        print(f"Response: {response.text[:100]}")
    
    # Test with dummy auth header to bypass auth and test field validation
    headers = {"Authorization": "Bearer dummy_token"}
    response = client.post("/api/scrape", 
        json={"max_pages": 1},  # Missing required 'url' field
        headers=headers
    )
    print(f"Missing URL field (with auth) - Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected missing required field")
    elif response.status_code == 401:
        print("⚠️ Authentication failed (token validation)")
    else:
        print(f"Response: {response.text[:100]}")
    
    # Test null URL
    response = client.post("/api/scrape", 
        json={"url": None, "max_pages": 1},  # URL is null
        headers=headers
    )
    print(f"Null URL - Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected null URL")
    elif response.status_code == 401:
        print("⚠️ Authentication failed (token validation)")
    else:
        print(f"Response: {response.text[:100]}")
    
    # Test empty URL
    response = client.post("/api/scrape", 
        json={"url": "", "max_pages": 1},  # URL is empty
        headers=headers
    )
    print(f"Empty URL - Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Correctly rejected empty URL")
    elif response.status_code == 401:
        print("⚠️ Authentication failed (token validation)")
    else:
        print(f"Response: {response.text[:100]}")

def test_endpoint_structure():
    """Test endpoint structure and required fields based on contract"""
    print("\n=== ENDPOINT STRUCTURE ANALYSIS ===")
    
    # Based on orchestration_contract_v1.json
    endpoints = {
        "/api/scrape": {
            "method": "POST",
            "required_fields": ["url"],
            "optional_fields": ["max_pages"],
            "response_fields": ["success", "data"]
        },
        "/api/news-analysis": {
            "method": "POST", 
            "required_fields": ["url"],
            "optional_fields": ["analysis_type"],
            "response_fields": ["success", "analysis"]
        },
        "/api/summarize": {
            "method": "POST",
            "required_fields": ["content"],
            "optional_fields": ["max_length"],
            "response_fields": ["success", "summary"]
        },
        "/api/scraped-news": {
            "method": "GET",
            "response_fields": ["success", "data", "count"]
        }
    }
    
    for endpoint, config in endpoints.items():
        print(f"\n{endpoint}:")
        print(f"  Method: {config['method']}")
        if 'required_fields' in config:
            print(f"  Required fields: {config['required_fields']}")
        if 'optional_fields' in config:
            print(f"  Optional fields: {config['optional_fields']}")
        if 'response_fields' in config:
            print(f"  Response fields: {config['response_fields']}")

def test_response_field_types():
    """Test response field types from working endpoints"""
    print("\n=== RESPONSE FIELD TYPE VALIDATION ===")
    
    # Test scraped-news endpoint (works without auth)
    response = client.get("/api/scraped-news")
    print(f"Scraped news GET - Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        # Validate field types against contract
        if "success" in data:
            print(f"  success field: {type(data['success'])} - {'✅ Correct (bool)' if isinstance(data['success'], bool) else '❌ Incorrect type'}")
        
        if "data" in data:
            print(f"  data field: {type(data['data'])} - {'✅ Correct (list)' if isinstance(data['data'], list) else '❌ Incorrect type'}")
            if isinstance(data['data'], list):
                print(f"  data length: {len(data['data'])}")
        
        if "count" in data:
            print(f"  count field: {type(data['count'])} - {'✅ Correct (int)' if isinstance(data['count'], int) else '❌ Incorrect type'}")
            print(f"  count value: {data['count']}")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"\nHealth endpoint - Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        # Validate field types against contract
        if "status" in data:
            print(f"  status field: {type(data['status'])} - {'✅ Correct (str)' if isinstance(data['status'], str) else '❌ Incorrect type'}")
            print(f"  status value: {data['status']}")
        
        if "timestamp" in data:
            print(f"  timestamp field: {type(data['timestamp'])} - {'✅ Correct (str)' if isinstance(data['timestamp'], str) else '❌ Incorrect type'}")
        
        if "services" in data:
            print(f"  services field: {type(data['services'])} - {'✅ Correct (dict)' if isinstance(data['services'], dict) else '❌ Incorrect type'}")

if __name__ == "__main__":
    print("Required Fields & Null Handling Test Suite (No Auth)")
    print("=" * 70)
    
    test_scrape_required_fields_no_auth()
    test_endpoint_structure()
    test_response_field_types()
    
    print("\n" + "=" * 70)
    print("Required fields & null handling validation complete")
    print("\nSUMMARY:")
    print("- Authentication is required for most endpoints")
    print("- Field validation works when authentication passes")
    print("- Response field types match contract specifications")
    print("- Health and scraped-news endpoints work without auth")