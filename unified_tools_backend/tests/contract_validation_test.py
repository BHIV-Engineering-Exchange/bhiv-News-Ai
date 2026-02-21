import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, get_db
from database import DatabaseManager

# Use a test-specific database
TEST_DB_PATH = "contract_test.db"

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

def test_health_endpoint_contract():
    """Test health endpoint contract adherence"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check required fields
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data
    
    # Check field types
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["services"], dict)
    
    # Check status value
    assert data["status"] == "healthy"
    
    # Check timestamp format (ISO 8601)
    try:
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("Timestamp is not in ISO 8601 format")

def test_scrape_endpoint_contract(db_manager: DatabaseManager):
    """Test scrape endpoint contract adherence"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/scrape", json={"url": "https://www.bbc.com/news/world-us-canada-68515807", "max_pages": 1}, headers=headers)
    
    # Check response structure
    assert response.status_code in [200, 400, 422]  # Acceptable status codes
    
    data = response.json()
    
    # Check required fields based on contract
    assert "success" in data
    assert isinstance(data["success"], bool)
    
    if data["success"]:
        assert "data" in data
        # Check data structure
        assert isinstance(data["data"], dict)
        # Check for expected content fields
        if "content" in data["data"]:
            assert isinstance(data["data"]["content"], str)
    else:
        # If not successful, should have error details
        assert "detail" in data or "error" in data

def test_news_analysis_endpoint_contract(db_manager: DatabaseManager):
    """Test news analysis endpoint contract adherence"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/news-analysis", json={"url": "https://www.bbc.com/news/world-us-canada-68515807"}, headers=headers)
    
    # Check response structure
    assert response.status_code in [200, 400, 422]  # Acceptable status codes
    
    data = response.json()
    
    # Check required fields based on contract
    assert "success" in data
    assert isinstance(data["success"], bool)
    
    if data["success"]:
        assert "analysis" in data
        # Check analysis structure
        assert isinstance(data["analysis"], dict)
        # Check for expected analysis fields
        expected_fields = ["summary", "sentiment", "authenticity_score", "key_topics"]
        for field in expected_fields:
            if field in data["analysis"]:
                assert data["analysis"][field] is not None
    else:
        # If not successful, should have error details
        assert "detail" in data or "error" in data

def test_summarize_endpoint_contract():
    """Test summarize endpoint contract adherence"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    test_content = "This is a test article about artificial intelligence and its impact on society. The article discusses various applications and ethical considerations."
    
    response = client.post("/api/summarize", json={"content": test_content, "max_length": 100}, headers=headers)
    
    # Check response structure
    assert response.status_code in [200, 400, 422]  # Acceptable status codes
    
    data = response.json()
    
    # Check required fields based on contract
    assert "success" in data
    assert isinstance(data["success"], bool)
    
    if data["success"]:
        assert "summary" in data
        assert isinstance(data["summary"], str)
        assert len(data["summary"]) > 0  # Summary should not be empty
    else:
        # If not successful, should have error details
        assert "detail" in data or "error" in data

def test_scraped_news_get_contract(db_manager: DatabaseManager):
    """Test scraped news GET endpoint contract adherence"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/scraped-news", headers=headers)
    
    # Check response structure
    assert response.status_code == 200
    
    data = response.json()
    
    # Check required fields based on contract
    assert "success" in data
    assert isinstance(data["success"], bool)
    
    if data["success"]:
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "count" in data
        assert isinstance(data["count"], int)
        
        # Check data items structure
        for item in data["data"]:
            assert isinstance(item, dict)
            # Check for expected fields in news items
            expected_fields = ["id", "title", "content", "url", "scraped_at"]
            for field in expected_fields:
                if field in item:
                    assert item[field] is not None

def test_null_handling_in_responses():
    """Test that null values are handled properly in responses"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with empty content
    response = client.post("/api/summarize", json={"content": "", "max_length": 100}, headers=headers)
    data = response.json()
    
    # Should handle empty content gracefully
    assert "success" in data
    assert isinstance(data["success"], bool)
    
    if not data["success"]:
        # Should provide clear error message
        assert "detail" in data or "error" in data

def test_required_fields_validation():
    """Test that required fields are properly validated"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test missing required fields
    response = client.post("/api/scrape", json={}, headers=headers)
    assert response.status_code == 422
    
    data = response.json()
    assert "detail" in data
    
    # Test missing required fields in summarize
    response = client.post("/api/summarize", json={}, headers=headers)
    assert response.status_code == 422
    
    data = response.json()
    assert "detail" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])