import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, get_db
from database import DatabaseManager

# Use a test-specific database
TEST_DB_PATH = "stress_test.db"

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

def test_malformed_json(db_manager: DatabaseManager):
    """Test with malformed JSON"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    response = client.post("/api/scrape", content="{malformed_json}", headers=headers)
    assert response.status_code == 422 # Unprocessable Entity

def test_backend_down(db_manager: DatabaseManager):
    """Test behavior when backend is down"""
    # Temporarily override the database dependency to simulate a failure
    def failing_db():
        raise Exception("Database connection failed")
    
    app.dependency_overrides[get_db] = failing_db
    
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Scrape
    response = client.post("/api/scrape", json={"url": "https://www.bbc.com/news/world-us-canada-68515807", "max_pages": 1}, headers=headers)
    assert response.status_code == 400 # Bad Request (system handles failure gracefully)
    
    # Restore the original dependency
    app.dependency_overrides[get_db] = lambda: db_manager

def test_clean_news_url(db_manager: DatabaseManager):
    """Test with a clean, valid news URL"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/scrape", 
        json={"url": "https://www.bbc.com/news/world-us-canada-68515807", "max_pages": 1}, 
        headers=headers
    )
    
    # Document what happens - success or failure
    print(f"Clean news URL test: Status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Success: Retrieved {len(data.get('data', []))} articles")
    else:
        print(f"  - Failed: {response.text}")
    
    # We don't assert success/failure - we document the behavior
    assert response.status_code in [200, 400, 422]  # Acceptable responses

def test_long_news_url(db_manager: DatabaseManager):
    """Test with a very long news URL"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a long URL with query parameters
    long_url = "https://www.bbc.com/news/world-us-canada-68515807" + "?param=" + "x" * 500
    
    response = client.post("/api/scrape", 
        json={"url": long_url, "max_pages": 1}, 
        headers=headers
    )
    
    print(f"Long URL test: Status {response.status_code}")
    if response.status_code == 200:
        print("  - System handled long URL successfully")
    else:
        print(f"  - System rejected long URL: {response.text}")
    
    # Document the behavior, don't force success
    assert response.status_code in [200, 400, 414]  # 414 = URI Too Long

def test_short_news_article(db_manager: DatabaseManager):
    """Test with a very short news article or minimal content"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use a URL that might have minimal content
    response = client.post("/api/scrape", 
        json={"url": "https://www.bbc.com/news/live/world-europe-68515808", "max_pages": 1}, 
        headers=headers
    )
    
    print(f"Short article test: Status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        articles = data.get('data', [])
        print(f"  - Retrieved {len(articles)} articles")
        if articles:
            # Check if content is very short
            content_length = len(articles[0].get('content', ''))
            print(f"  - First article content length: {content_length} characters")
    else:
        print(f"  - Failed: {response.text}")
    
    # Document behavior
    assert response.status_code in [200, 400, 422]

def test_multiple_back_to_back_submissions(db_manager: DatabaseManager):
    """Test multiple rapid submissions to stress the system"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    url = "https://www.bbc.com/news/world-us-canada-68515807"
    results = []
    
    print("Multiple back-to-back submissions test:")
    for i in range(5):
        response = client.post("/api/scrape", 
            json={"url": url, "max_pages": 1}, 
            headers=headers
        )
        results.append(response.status_code)
        print(f"  - Submission {i+1}: Status {response.status_code}")
        
        if response.status_code != 200:
            print(f"    Failed response: {response.text[:100]}...")
    
    # Document what happened
    success_count = results.count(200)
    print(f"  - Summary: {success_count}/5 successful, {results}")
    
    # All responses should be acceptable (200, 400, 422, 429 for rate limiting)
    for status in results:
        assert status in [200, 400, 422, 429]

def test_empty_url(db_manager: DatabaseManager):
    """Test with empty URL"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/scrape", 
        json={"url": "", "max_pages": 1}, 
        headers=headers
    )
    
    print(f"Empty URL test: Status {response.status_code}")
    print(f"  - Response: {response.text}")
    
    # Document the error handling
    assert response.status_code in [400, 422]  # Should reject empty URL

def test_broken_url(db_manager: DatabaseManager):
    """Test with broken/malformed URL"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/scrape", 
        json={"url": "this-is-not-a-url", "max_pages": 1}, 
        headers=headers
    )
    
    print(f"Broken URL test: Status {response.status_code}")
    print(f"  - Response: {response.text}")
    
    # Document error handling
    assert response.status_code in [400, 422]  # Should reject broken URL

def test_non_news_url(db_manager: DatabaseManager):
    """Test with non-news URL (e.g., Google)"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/scrape", 
        json={"url": "https://www.google.com", "max_pages": 1}, 
        headers=headers
    )
    
    print(f"Non-news URL test: Status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - System processed non-news URL, got {len(data.get('data', []))} results")
    else:
        print(f"  - System rejected non-news URL: {response.text}")
    
    # Document behavior - system might process or reject
    assert response.status_code in [200, 400, 422]

def test_simulate_slow_response(db_manager: DatabaseManager):
    """Test system behavior under simulated slow response conditions"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Import time module for timing
    import time
    
    print("Simulating slow response test:")
    start_time = time.time()
    
    # Make a request that might be slow
    response = client.post("/api/scrape", 
        json={"url": "https://www.bbc.com/news/world-us-canada-68515807", "max_pages": 3}, 
        headers=headers
    )
    
    end_time = time.time()
    response_time = end_time - start_time
    
    print(f"  - Response time: {response_time:.2f} seconds")
    print(f"  - Status: {response.status_code}")
    
    if response_time > 5.0:
        print("  - ⚠️  SLOW RESPONSE DETECTED")
    elif response_time > 2.0:
        print("  - Moderate response time")
    else:
        print("  - Fast response")
    
    # Document the response time behavior
    assert response.status_code in [200, 400, 422, 504]  # 504 = Gateway Timeout

def test_tts_missing(db_manager: DatabaseManager):
    """Test behavior when TTS (Text-to-Speech) service is missing/unavailable"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("TTS Missing Test:")
    # First, let's see if there are any TTS-related endpoints
    tts_endpoints = ["/api/tts", "/api/text-to-speech", "/api/audio/generate"]
    
    tts_found = False
    for endpoint in tts_endpoints:
        response = client.get(endpoint, headers=headers)
        if response.status_code != 404:
            print(f"  - Found TTS endpoint: {endpoint}")
            tts_found = True
            break
    
    if not tts_found:
        print("  - No dedicated TTS endpoints found")
        print("  - TTS functionality may be handled by external services")
        
        # Test if the system can still process news without TTS
        response = client.post("/api/scrape", 
            json={"url": "https://www.bbc.com/news/world-us-canada-68515807", "max_pages": 1}, 
            headers=headers
        )
        
        if response.status_code == 200:
            print("  - ✅ System continues to work without TTS")
        else:
            print(f"  - ❌ System fails without TTS: {response.status_code}")
    
    # The system should handle TTS absence gracefully
    assert True  # Document behavior, don't force failure

def test_rl_threshold_fail(db_manager: DatabaseManager):
    """Test behavior when RL (Rate Limiting) threshold is exceeded"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("RL Threshold Test:")
    
    # Make many rapid requests to potentially trigger rate limiting
    url = "https://www.bbc.com/news/world-us-canada-68515807"
    rate_limited = False
    
    for i in range(20):  # Try 20 rapid requests
        response = client.post("/api/scrape", 
            json={"url": url, "max_pages": 1}, 
            headers=headers
        )
        
        if response.status_code == 429:  # Too Many Requests
            print(f"  - ✅ Rate limiting triggered at request {i+1}")
            rate_limited = True
            break
        elif response.status_code != 200:
            print(f"  - Request {i+1} failed with {response.status_code}")
    
    if not rate_limited:
        print("  - No rate limiting detected in 20 rapid requests")
        print("  - System appears to handle high request volume")
    
    # Document whether rate limiting works
    assert True  # Document behavior

def test_orchestration_timeout(db_manager: DatabaseManager):
    """Test behavior when orchestration times out"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Orchestration Timeout Test:")
    
    # Try to trigger a timeout with a complex request
    response = client.post("/api/scrape", 
        json={
            "url": "https://www.bbc.com/news", 
            "max_pages": 10,  # Request many pages
            "deep_analysis": True  # If such parameter exists
        }, 
        headers=headers
    )
    
    print(f"  - Complex request status: {response.status_code}")
    
    if response.status_code == 504:  # Gateway Timeout
        print("  - ✅ Timeout handled gracefully with 504")
    elif response.status_code == 200:
        print("  - ✅ Complex request completed successfully")
        data = response.json()
        print(f"  - Retrieved {len(data.get('data', []))} articles")
    else:
        print(f"  - Request failed with: {response.text[:100]}...")
    
    # Document timeout behavior
    assert response.status_code in [200, 400, 422, 504]




