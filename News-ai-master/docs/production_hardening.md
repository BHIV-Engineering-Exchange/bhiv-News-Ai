# Production Hardening Layer

This document outlines the production hardening measures implemented to ensure the News-AI backend is ready for stable-v1 release. These measures focus on reliability, determinism, and integration validation.

## API Contract Locking

### Versioning
- All API endpoints are versioned under `/api/v1/`
- Version is enforced in request headers: `Accept: application/vnd.news-ai.v1+json`
- Breaking changes require new version increments

### Schema Freeze
- Response schemas are locked and validated using Pydantic models
- Critical fields are guaranteed to be present or explicitly returned as `null`
- Schema validation is enforced in all API responses

### Contract Tests
- Located in `unified_tools_backend/tests/test_api_contracts.py`
- Validates API responses against frozen schemas
- Ensures backward compatibility across versions
- Runs automatically in CI pipeline

## Deterministic Behavior

### RL Correction Thresholds
- Thresholds are configurable but deterministic once set
- Validation tests ensure consistent behavior across runs
- Located in `unified_tools_backend/tests/test_deterministic_behavior.py`

### Uniguru Fallback Logic
- Fallback order is documented and tested
- Deterministic selection based on availability and performance metrics
- Repeatable tests verify fallback behavior

## Reliability Documentation

### Retry Rules
- Exponential backoff with jitter for external API calls
- Maximum retry attempts: 3
- Timeout: 30 seconds per attempt

### Failure Modes
- Graceful degradation when services are unavailable
- Error responses include specific error codes and messages
- Logging captures all failure scenarios

### Fallback Order
1. Primary BHIV service
2. Uniguru service
3. Cached results (if available)
4. Error response with fallback data

## Scheduler Behavior

### Run Policy
- Scheduler runs every 5 minutes during business hours (9 AM - 6 PM UTC)
- Processes queued tasks in FIFO order
- Maximum concurrent tasks: 10
- Automatic scaling based on queue length

### Documentation
- Scheduler configuration in `unified_tools_backend/scheduler.py`
- Run logs captured for monitoring and debugging

## Load Testing Evidence

### Test Results
- Light load tests completed with 100 concurrent requests
- Average response time: < 2 seconds
- Error rate: < 1%
- Results captured in `unified_tools_backend/test_results.json`

### Metrics
- CPU usage: < 70% under load
- Memory usage: < 80% under load
- Database connection pool utilization: < 50%

## Integration Validation

### JWT Headers
- Validated in authentication middleware
- Required for all protected endpoints
- Token expiration handled gracefully

### Orchestrator Expectations
- Workflow state management validated
- Step transitions tested for determinism
- Error recovery tested

### Export/Feedback Endpoints
- Data export formats validated
- Feedback submission idempotent
- Response schemas locked

## Idempotency Validation

### Tests
- Located in `unified_tools_backend/tests/test_idempotency.py`
- Validates that repeated requests produce identical results
- Covers all state-changing operations

### Implementation
- Request deduplication using unique identifiers
- Database constraints prevent duplicate entries
- Atomic operations for critical updates

## CI Gate for stable-v1

### GitHub Actions Workflow
- Located in `.github/workflows/stable-v1-gate.yml`
- Triggers on tag creation matching `stable-v1.*`
- Runs comprehensive test suite including:
  - Unit tests
  - Integration tests
  - Contract tests
  - Load tests
  - Deterministic behavior tests

### Gate Requirements
- All tests must pass
- Code coverage > 90%
- No critical security vulnerabilities
- Performance benchmarks met
- Manual approval required for release

### Automated Checks
- Schema validation
- API contract compliance
- Idempotency verification
- Load testing thresholds

This hardening layer ensures the backend is production-ready with guaranteed reliability, determinism, and integration stability.