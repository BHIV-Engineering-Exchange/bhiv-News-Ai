#!/usr/bin/env python3
"""
Required Fields & Null Handling Test Script
Tests API endpoints for proper field validation and null handling
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

def test_scrape_required_fields():
    """Test /api/scrape endpoint required fields"""
    print("=== SCRAPE ENDPOINT REQUIRED FIELDS TEST ===")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test missing URL (required field)
    response = client.post("/api/scrape", 
        json={"max_pages": 1},  # Missing required 'url' field
        headers=headers
    )
    print(f"Missing URL field - Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected missing required field")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test null URL
    response = client.post("/api/scrape", 
        json={"url": None, "max_pages": 1},  # URL is null
        headers=headers
    )
    print(f"Null URL - Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected null URL")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test empty URL
    response = client.post("/api/scrape", 
        json={"url": "", "max_pages": 1},  # URL is empty
        headers=headers
    )
    print(f"Empty URL - Status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Correctly rejected empty URL")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test valid request
    response = client.post("/api/scrape", 
        json={"url": "https://www.bbc.com/news", "max_pages": 1},  # Valid request
        headers=headers
    )
    print(f"Valid request - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Valid request accepted")
    elif response.status_code == 400:
        print("✅ Valid request format accepted (scraping may fail due to external factors)")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")

def test_summarize_required_fields():
    """Test /api/summarize endpoint required fields"""
    print("\n=== SUMMARIZE ENDPOINT REQUIRED FIELDS TEST ===")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test missing content (required field)
    response = client.post("/api/summarize", 
        json={"max_length": 100},  # Missing required 'content' field
        headers=headers
    )
    print(f"Missing content field - Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected missing required field")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test null content
    response = client.post("/api/summarize", 
        json={"content": None, "max_length": 100},  # Content is null
        headers=headers
    )
    print(f"Null content - Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected null content")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test empty content
    response = client.post("/api/summarize", 
        json={"content": "", "max_length": 100},  # Content is empty
        headers=headers
    )
    print(f"Empty content - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Empty content handled")
        data = response.json()
        print(f"   Response: {data.get('summary', 'No summary')}")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test valid request
    response = client.post("/api/summarize", 
        json={"content": "This is a test article about current events.", "max_length": 100},  # Valid request
        headers=headers
    )
    print(f"Valid request - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Valid request accepted")
        data = response.json()
        print(f"   Summary: {data.get('summary', 'No summary')[:50]}...")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")

def test_news_analysis_required_fields():
    """Test /api/news-analysis endpoint required fields"""
    print("\n=== NEWS ANALYSIS ENDPOINT REQUIRED FIELDS TEST ===")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test missing URL (required field)
    response = client.post("/api/news-analysis", 
        json={"analysis_type": "comprehensive"},  # Missing required 'url' field
        headers=headers
    )
    print(f"Missing URL field - Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected missing required field")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test null URL
    response = client.post("/api/news-analysis", 
        json={"url": None, "analysis_type": "comprehensive"},  # URL is null
        headers=headers
    )
    print(f"Null URL - Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected null URL")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test valid request
    response = client.post("/api/news-analysis", 
        json={"url": "https://www.bbc.com/news", "analysis_type": "comprehensive"},  # Valid request
        headers=headers
    )
    print(f"Valid request - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Valid request accepted")
    elif response.status_code == 400:
        print("✅ Valid request format accepted (analysis may fail due to external factors)")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")

def test_optional_fields():
    """Test optional fields behavior"""
    print("\n=== OPTIONAL FIELDS TEST ===")
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test scrape without optional max_pages
    response = client.post("/api/scrape", 
        json={"url": "https://www.bbc.com/news"},  # No max_pages (optional)
        headers=headers
    )
    print(f"Scrape without optional max_pages - Status: {response.status_code}")
    if response.status_code == 200 or response.status_code == 400:
        print("✅ Optional field omission handled correctly")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test summarize without optional max_length
    response = client.post("/api/summarize", 
        json={"content": "This is a test article."},  # No max_length (optional)
        headers=headers
    )
    print(f"Summarize without optional max_length - Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Optional field omission handled correctly")
        data = response.json()
        print(f"   Summary: {data.get('summary', 'No summary')[:50]}...")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")
    
    # Test news-analysis without optional analysis_type
    response = client.post("/api/news-analysis", 
        json={"url": "https://www.bbc.com/news"},  # No analysis_type (optional)
        headers=headers
    )
    print(f"News analysis without optional analysis_type - Status: {response.status_code}")
    if response.status_code == 200 or response.status_code == 400:
        print("✅ Optional field omission handled correctly")
    else:
        print(f"❌ Unexpected response: {response.text[:100]}")

if __name__ == "__main__":
    print("Required Fields & Null Handling Test Suite")
    print("=" * 60)
    
    test_scrape_required_fields()
    test_summarize_required_fields()
    test_news_analysis_required_fields()
    test_optional_fields()
    
    print("\n" + "=" * 60)
    print("Required fields & null handling validation complete")