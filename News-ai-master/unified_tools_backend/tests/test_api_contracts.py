"""
API Contract Tests for Backend Hardening
Tests API versioning, schema freeze, and response validation
"""
import pytest
import json
from fastapi.testclient import TestClient
from app.api.main import app
from pydantic import ValidationError
import jsonschema


class TestAPIContractLocking:
    """Test API contract locking and versioning"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_api_version_headers(self):
        """Test that all responses include API version headers"""
        response = self.client.get("/health")

        assert response.status_code == 200
        assert "X-API-Version" in response.headers
        assert response.headers["X-API-Version"] == "v1.0.0"
        assert "X-Schema-Frozen" in response.headers
        assert response.headers["X-Schema-Frozen"] == "true"

    def test_health_response_schema(self):
        """Test health endpoint response matches schema"""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Required fields
        required_fields = ["status", "timestamp", "version", "environment", "uptime", "services", "system_info", "sprint_status", "production_ready"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Validate services structure
        services = data["services"]
        expected_services = ["database", "uniguru", "bhiv_core", "websocket", "agents", "rl_feedback", "automator"]
        for service in expected_services:
            assert service in services, f"Missing service: {service}"
            assert "status" in services[service]
            assert "details" in services[service]

    def test_unified_pipeline_request_validation(self):
        """Test unified pipeline request validation"""
        # Valid request
        valid_request = {
            "url": "https://example.com/news",
            "options": {
                "enable_bhiv_push": True,
                "enable_audio": True,
                "channels": ["news_channel_1"],
                "avatars": ["avatar_alice"],
                "voice": "default",
                "force_correction": False,
                "tone": "neutral",
                "language": "en",
                "avatar_ready": True
            }
        }

        response = self.client.post("/v1/run_pipeline", json=valid_request)
        assert response.status_code == 200

        data = response.json()
        required_fields = ["success", "job_id", "status", "message", "check_status_url", "estimated_completion", "timestamp"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_unified_pipeline_invalid_request(self):
        """Test unified pipeline rejects invalid requests"""
        # Missing URL
        invalid_request = {"options": {}}

        response = self.client.post("/v1/run_pipeline", json=invalid_request)
        assert response.status_code == 400

    def test_bhiv_push_request_validation(self):
        """Test BHIV push request validation"""
        valid_request = {
            "channel": "news_channel_1",
            "avatar": "avatar_alice",
            "content": {"title": "Test News", "summary": "Test summary"}
        }

        response = self.client.post("/api/bhiv/push", json=valid_request)
        # May fail due to BHIV service not being mocked, but should validate schema
        assert response.status_code in [200, 500]  # 500 is acceptable if service fails

        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "data", "message", "timestamp"]
            for field in required_fields:
                assert field in data

    def test_agents_response_schema(self):
        """Test agents endpoint response schema"""
        response = self.client.get("/api/agents")

        assert response.status_code == 200
        data = response.json()

        required_fields = ["success", "data", "timestamp"]
        for field in required_fields:
            assert field in data

        # Check data structure
        agents_data = data["data"]
        assert "agents" in agents_data
        assert "total_agents" in agents_data
        assert "registry_status" in agents_data

        # Each agent should have required fields
        for agent in agents_data["agents"]:
            required_agent_fields = ["id", "name", "role", "capabilities", "priority", "status"]
            for field in required_agent_fields:
                assert field in agent, f"Agent missing field: {field}"

    def test_rl_metrics_response_schema(self):
        """Test RL metrics endpoint response schema"""
        response = self.client.get("/api/rl/metrics")

        assert response.status_code == 200
        data = response.json()

        required_fields = ["success", "data", "timestamp"]
        for field in required_fields:
            assert field in data

    def test_news_items_response_schema(self):
        """Test news items endpoint response schema"""
        response = self.client.get("/api/news")

        assert response.status_code == 200
        data = response.json()

        required_fields = ["success", "data", "count", "timestamp"]
        for field in required_fields:
            assert field in data

        assert isinstance(data["data"], list)
        assert data["count"] == len(data["data"])

    def test_queue_stats_response_schema(self):
        """Test queue stats endpoint response schema"""
        response = self.client.get("/api/queue/stats")

        assert response.status_code == 200
        data = response.json()

        required_fields = ["success", "data", "timestamp"]
        for field in required_fields:
            assert field in data

    def test_scheduler_stats_response_schema(self):
        """Test scheduler stats endpoint response schema"""
        response = self.client.get("/api/scheduler/stats")

        assert response.status_code == 200
        data = response.json()

        required_fields = ["success", "data", "timestamp"]
        for field in required_fields:
            assert field in data

    def test_openapi_spec_endpoint(self):
        """Test versioned OpenAPI spec endpoint"""
        response = self.client.get("/v1/openapi.json")

        assert response.status_code == 200
        spec = response.json()

        # Check OpenAPI structure
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec

        # Check contract metadata
        assert "x-api-contract" in spec["info"]
        contract = spec["info"]["x-api-contract"]
        assert contract["version"] == "v1.0.0"
        assert contract["frozen"] is True
        assert contract["enforced"] is True
        assert "last_updated" in contract
        assert contract["breaking_changes_allowed"] is False

    def test_contract_enforcement_headers(self):
        """Test that contract enforcement headers are present"""
        response = self.client.get("/health")

        assert response.status_code == 200
        assert "X-API-Version" in response.headers
        assert response.headers["X-API-Version"] == "v1.0.0"
        assert "X-Schema-Frozen" in response.headers
        assert response.headers["X-Schema-Frozen"] == "true"
        assert "X-Contract-Enforced" in response.headers
        assert response.headers["X-Contract-Enforced"] == "true"

    def test_websocket_stats_response_schema(self):
        """Test websocket stats endpoint response schema"""
        response = self.client.get("/api/websocket/stats")

        assert response.status_code == 200
        data = response.json()

        required_fields = ["success", "data", "timestamp"]
        for field in required_fields:
            assert field in data


class TestSchemaFreeze:
    """Test that schemas are frozen and don't change unexpectedly"""

    def setup_method(self):
        self.client = TestClient(app)

        # Define expected schemas for critical endpoints
        self.expected_schemas = {
            "health": {
                "type": "object",
                "required": ["status", "timestamp", "version", "environment", "uptime", "services", "system_info", "sprint_status", "production_ready"],
                "properties": {
                    "status": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "version": {"type": "string"},
                    "environment": {"type": "string"},
                    "uptime": {"type": "string"},
                    "services": {"type": "object"},
                    "system_info": {"type": "object"},
                    "sprint_status": {"type": "string"},
                    "production_ready": {"type": "boolean"}
                }
            },
            "agents": {
                "type": "object",
                "required": ["success", "data", "timestamp"],
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {
                        "type": "object",
                        "required": ["agents", "total_agents", "registry_status"],
                        "properties": {
                            "agents": {"type": "array"},
                            "total_agents": {"type": "integer"},
                            "registry_status": {"type": "string"}
                        }
                    },
                    "timestamp": {"type": "string"}
                }
            }
        }

    def test_health_schema_frozen(self):
        """Test health endpoint schema is frozen"""
        response = self.client.get("/health")
        assert response.status_code == 200

        data = response.json()
        try:
            jsonschema.validate(instance=data, schema=self.expected_schemas["health"])
        except jsonschema.ValidationError as e:
            pytest.fail(f"Health response schema changed: {e}")

    def test_agents_schema_frozen(self):
        """Test agents endpoint schema is frozen"""
        response = self.client.get("/api/agents")
        assert response.status_code == 200

        data = response.json()
        try:
            jsonschema.validate(instance=data, schema=self.expected_schemas["agents"])
        except jsonschema.ValidationError as e:
            pytest.fail(f"Agents response schema changed: {e}")


class TestAPIIdempotency:
    """Test API idempotency for critical operations"""

    def setup_method(self):
        self.client = TestClient(app)

    def test_health_idempotent(self):
        """Test health endpoint is idempotent"""
        # Multiple calls should return same structure
        responses = []
        for _ in range(3):
            response = self.client.get("/health")
            assert response.status_code == 200
            responses.append(response.json())

        # All responses should have same structure
        first_response = responses[0]
        for resp in responses[1:]:
            assert resp["status"] == first_response["status"]
            assert resp["version"] == first_response["version"]
            assert resp["production_ready"] == first_response["production_ready"]

    def test_agents_idempotent(self):
        """Test agents endpoint is idempotent"""
        responses = []
        for _ in range(3):
            response = self.client.get("/api/agents")
            assert response.status_code == 200
            responses.append(response.json())

        # All responses should have same agent count and structure
        first_response = responses[0]
        for resp in responses[1:]:
            assert resp["data"]["total_agents"] == first_response["data"]["total_agents"]
            assert len(resp["data"]["agents"]) == len(first_response["data"]["agents"])

    def test_unified_pipeline_idempotent(self):
        """Test unified pipeline endpoint is idempotent for same requests"""
        request_data = {
            "url": "https://example.com/test-news",
            "options": {
                "enable_bhiv_push": False,
                "enable_audio": False,
                "channels": ["test_channel"],
                "avatars": ["test_avatar"],
                "voice": "default",
                "force_correction": False,
                "tone": "neutral",
                "language": "en",
                "avatar_ready": True
            }
        }

        # Multiple identical requests should produce consistent responses
        responses = []
        for _ in range(3):
            response = self.client.post("/v1/run_pipeline", json=request_data)
            assert response.status_code == 200
            responses.append(response.json())

        # All responses should have same structure and success status
        first_response = responses[0]
        for resp in responses[1:]:
            assert resp["success"] == first_response["success"]
            assert resp["status"] == first_response["status"]
            assert "job_id" in resp
            assert "check_status_url" in resp

    def test_rl_feedback_idempotent(self):
        """Test RL feedback endpoint is idempotent"""
        feedback_data = {
            "job_id": "test_job_123",
            "feedback": {
                "rating": 4.5,
                "comments": "Test feedback",
                "corrections": ["minor_adjustment"],
                "performance_metrics": {
                    "accuracy": 0.95,
                    "speed": 0.85
                }
            }
        }

        responses = []
        for _ in range(3):
            response = self.client.post("/api/rl/feedback", json=feedback_data)
            assert response.status_code in [200, 201]  # Accept created or ok
            responses.append(response.json())

        # All responses should have consistent structure
        first_response = responses[0]
        for resp in responses[1:]:
            assert resp["success"] == first_response["success"]
            assert "message" in resp

    def test_bhiv_push_idempotent(self):
        """Test BHIV push endpoint is idempotent"""
        push_data = {
            "channel": "test_channel",
            "avatar": "test_avatar",
            "content": {
                "title": "Test News Title",
                "summary": "Test summary content",
                "url": "https://example.com/news"
            }
        }

        responses = []
        for _ in range(3):
            response = self.client.post("/api/bhiv/push", json=push_data)
            # May return 500 if BHIV service not available, but should be consistent
            responses.append(response.status_code)

        # All responses should have same status code
        first_status = responses[0]
        for status in responses[1:]:
            assert status == first_status

    def test_queue_stats_idempotent(self):
        """Test queue stats endpoint is idempotent"""
        responses = []
        for _ in range(3):
            response = self.client.get("/api/queue/stats")
            assert response.status_code == 200
            responses.append(response.json())

        # Structure should be consistent
        first_response = responses[0]
        for resp in responses[1:]:
            assert resp["success"] == first_response["success"]
            assert "data" in resp

    def test_scheduler_stats_idempotent(self):
        """Test scheduler stats endpoint is idempotent"""
        responses = []
        for _ in range(3):
            response = self.client.get("/api/scheduler/stats")
            assert response.status_code == 200
            responses.append(response.json())

        # Structure should be consistent
        first_response = responses[0]
        for resp in responses[1:]:
            assert resp["success"] == first_response["success"]
            assert "data" in resp