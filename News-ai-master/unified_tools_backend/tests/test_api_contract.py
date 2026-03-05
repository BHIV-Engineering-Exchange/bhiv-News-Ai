"""
API Contract and Determinism Tests for News AI Backend v1.0.0

This module contains tests to ensure:
1. API responses conform to locked v1.0.0 schemas
2. All required fields are present in responses
3. Responses are deterministic across identical requests
4. Schema versioning is enforced
"""

from datetime import datetime
from pydantic import ValidationError

# Import the API models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.main import (
    HealthResponse, AgentsResponse, UnifiedPipelineResponse
)


class TestAPIContractValidation:
    """Test API contract compliance and determinism"""

    def test_health_response_contract(self):
        """Test HealthResponse conforms to v1.0.0 contract"""
        response = HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            environment="test",
            uptime="unknown",
            services={
                "database": {"status": "healthy", "details": "connected"},
                "uniguru": {"status": "configured", "details": "API key set"}
            },
            system_info={"debug": False},
            sprint_status="stable",
            production_ready=True
        )

        # Verify all required fields are present
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.api_version == "v1.0.0"
        assert response.schema_frozen == True
        assert "database" in response.services
        assert "uniguru" in response.services

    def test_agents_response_contract(self):
        """Test AgentsResponse conforms to contract"""
        response = AgentsResponse(
            success=True,
            data={
                "agents": [
                    {
                        "id": "fetch_agent",
                        "name": "News Fetch Agent",
                        "role": "fetch",
                        "capabilities": ["web_scraping"],
                        "priority": 1,
                        "status": "active"
                    }
                ],
                "total_agents": 1,
                "registry_status": "active"
            },
            timestamp=datetime.now().isoformat()
        )

        assert response.success == True
        assert response.api_version == "v1.0.0"
        assert response.schema_frozen == True
        assert len(response.data["agents"]) == 1
        assert response.data["total_agents"] == 1

    def test_response_schema_immutability(self):
        """Test that response schemas cannot be modified without version bump"""
        response = HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            environment="test",
            uptime="unknown",
            services={},
            system_info={},
            sprint_status="stable",
            production_ready=True
        )

        # These fields must always be present in v1.0.0
        required_fields = [
            "status", "timestamp", "version", "environment", "uptime",
            "services", "system_info", "sprint_status", "production_ready",
            "api_version", "schema_frozen"
        ]

        response_dict = response.dict()
        for field in required_fields:
            assert field in response_dict, f"Required field '{field}' missing from response"

        # api_version must be "v1.0.0"
        assert response_dict["api_version"] == "v1.0.0"

        # schema_frozen must be True
        assert response_dict["schema_frozen"] == True

    def test_deterministic_response_structure(self):
        """Test that identical inputs produce identical response structures"""
        timestamp = datetime.now().isoformat()

        response1 = HealthResponse(
            status="healthy",
            timestamp=timestamp,
            version="1.0.0",
            environment="test",
            uptime="unknown",
            services={"test": {"status": "ok"}},
            system_info={"debug": False},
            sprint_status="stable",
            production_ready=True
        )

        response2 = HealthResponse(
            status="healthy",
            timestamp=timestamp,
            version="1.0.0",
            environment="test",
            uptime="unknown",
            services={"test": {"status": "ok"}},
            system_info={"debug": False},
            sprint_status="stable",
            production_ready=True
        )

        # Responses should be structurally identical
        dict1 = response1.dict()
        dict2 = response2.dict()

        # Compare all fields except potentially dynamic ones
        for key in dict1:
            if key not in ["timestamp"]:  # Exclude potentially dynamic fields
                assert dict1[key] == dict2[key], f"Field '{key}' differs between responses"

    def test_api_version_consistency(self):
        """Test that all responses use consistent API versioning"""
        responses = [
            HealthResponse(status="healthy", timestamp=datetime.now().isoformat(), version="1.0.0", environment="test", uptime="unknown", services={}, system_info={}, sprint_status="stable", production_ready=True),
            AgentsResponse(success=True, data={"agents": [], "total_agents": 0, "registry_status": "active"}, timestamp=datetime.now().isoformat()),
        ]

        for response in responses:
            assert response.api_version == "v1.0.0", f"Response {type(response).__name__} has incorrect API version"
            assert response.schema_frozen == True, f"Response {type(response).__name__} schema not frozen"


class TestDeterminismValidation:
    """Test deterministic behavior across multiple runs"""

    def test_multiple_health_responses_identical(self):
        """Test that multiple health responses with same input are identical"""
        responses = []

        for i in range(5):
            response = HealthResponse(
                status="healthy",
                timestamp="2025-01-01T00:00:00.000000",  # Fixed timestamp for determinism
                version="1.0.0",
                environment="test",
                uptime="unknown",
                services={
                    "database": {"status": "healthy", "details": "connected"},
                    "uniguru": {"status": "configured", "details": "API key set"}
                },
                system_info={"debug": False, "rate_limit": 100},
                sprint_status="stable",
                production_ready=True
            )
            responses.append(response.dict())

        # All responses should be identical
        for i in range(1, len(responses)):
            assert responses[0] == responses[i], f"Response {i} differs from first response"


if __name__ == "__main__":
    # Run basic validation
    test_instance = TestAPIContractValidation()
    determinism_test = TestDeterminismValidation()

    print("Running API Contract Validation Tests...")

    try:
        test_instance.test_health_response_contract()
        print("+ Health response contract test passed")

        test_instance.test_agents_response_contract()
        print("+ Agents response contract test passed")

        test_instance.test_response_schema_immutability()
        print("+ Response schema immutability test passed")

        test_instance.test_deterministic_response_structure()
        print("+ Deterministic response structure test passed")

        test_instance.test_api_version_consistency()
        print("+ API version consistency test passed")

        determinism_test.test_multiple_health_responses_identical()
        print("+ Multiple health responses determinism test passed")

        print("\n*** All API contract and determinism tests passed! ***")
        print("API v1.0.0 contract is locked and deterministic.")

    except Exception as e:
        print(f"*** Test failed: {e} ***")
        raise