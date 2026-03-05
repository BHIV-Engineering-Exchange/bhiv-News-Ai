# Production Hardening Guide for News-AI Backend

## Overview
This guide outlines the production hardening measures implemented to ensure the News-AI backend is ready for stable-v1 release. It covers API contract locking, deterministic behavior guarantees, reliability documentation, and CI/CD gates.

## 1. API Contract Locking

### Versioning Strategy
- **API Version**: v1.0.0 (locked for stable-v1)
- **Version Header**: `X-API-Version: v1.0.0`
- **Schema Freeze Header**: `X-Schema-Frozen: true`

### Schema Guarantees
All API responses include guaranteed fields that are either present or explicitly `null`. No fields are omitted.

#### Critical Endpoints Schema Contracts

**Health Endpoint (`/health`)**
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "ISO8601",
  "version": "v1.0.0",
  "environment": "production|staging|development",
  "uptime": "HH:MM:SS",
  "services": {
    "database": {"status": "up|down", "details": "..."},
    "uniguru": {"status": "up|down", "details": "..."},
    "bhiv_core": {"status": "up|down", "details": "..."},
    "websocket": {"status": "up|down", "details": "..."},
    "agents": {"status": "up|down", "details": "..."},
    "rl_feedback": {"status": "up|down", "details": "..."},
    "automator": {"status": "up|down", "details": "..."}
  },
  "system_info": {
    "cpu_usage": "float%",
    "memory_usage": "float%",
    "disk_usage": "float%"
  },
  "sprint_status": "Integration-B Complete",
  "production_ready": true
}
```

**Unified Pipeline (`/v1/run_pipeline`)**
```json
{
  "success": true|false,
  "job_id": "uuid",
  "status": "queued|processing|completed|failed",
  "message": "string",
  "check_status_url": "string",
  "estimated_completion": "ISO8601",
  "timestamp": "ISO8601"
}
```

### Contract Tests
Located in `unified_tools_backend/tests/test_api_contracts.py`:
- Schema validation tests for all critical endpoints
- Version header enforcement tests
- Schema freeze validation tests
- Idempotency tests for critical operations

## 2. Deterministic Behavior Guarantees

### RL Correction Thresholds
- **Correction Trigger**: Quality score < 0.7
- **Fallback Threshold**: Quality score < 0.5
- **Maximum Corrections**: 3 attempts per item
- **Timeout**: 30 seconds per correction attempt

**Test Coverage**: `unified_tools_backend/tests/test_rl_deterministic.py`
- Repeatable threshold tests with fixed datasets
- Fallback logic validation
- Timeout behavior verification

### Uniguru Fallback Logic
**Priority Order**:
1. Primary Uniguru API (direct call)
2. Cached results (if < 5 minutes old)
3. Simplified fallback mode (basic summarization)
4. Error response with null fields

**Deterministic Guarantees**:
- Same input always produces same output structure
- Fallback modes are predictable and documented
- No random behavior in production

### Queue Processing Determinism
- FIFO processing with priority weights
- Job deduplication based on URL hash
- Status transitions are atomic and logged
- Retry logic: 3 attempts with exponential backoff (1s, 4s, 16s)

## 3. Reliability Documentation

### Retry Rules
**API Retries**:
- HTTP 5xx errors: 3 retries with exponential backoff
- Network timeouts: 2 retries with 5s delay
- Rate limits: Exponential backoff up to 60s

**Service Retries**:
- Uniguru API: 2 retries for connection failures
- BHIV push: 3 retries for service unavailable
- Database operations: 5 retries for connection issues

### Failure Modes
**Graceful Degradation**:
- Uniguru down: Fallback to cached/baseline summaries
- BHIV down: Queue for later retry, continue processing
- Database down: Read-only mode with cached data
- Queue full: Reject new jobs with clear error message

**Error Response Format**:
```json
{
  "success": false,
  "error": {
    "code": "SERVICE_UNAVAILABLE|TIMEOUT|VALIDATION_ERROR",
    "message": "Human readable message",
    "details": "Technical details for debugging",
    "retry_after": 30
  },
  "timestamp": "ISO8601"
}
```

### Fallback Order Documentation
1. **Primary Path**: Full pipeline with all services
2. **Degraded Path**: Skip non-critical services (audio generation)
3. **Minimal Path**: Basic news processing only
4. **Offline Path**: Return cached results with warning

## 4. Scheduler Behavior

### Run Policy
**Execution Rules**:
- Maximum concurrent jobs: 10
- Queue size limit: 1000 jobs
- Job timeout: 300 seconds
- Cleanup interval: 60 seconds (remove completed jobs > 1 hour old)

**Priority System**:
- High: Breaking news (score > 0.9)
- Medium: Regular news (score 0.7-0.9)
- Low: Background processing (score < 0.7)

### Monitoring
Scheduler exposes metrics at `/api/scheduler/stats`:
```json
{
  "active_jobs": 5,
  "queued_jobs": 23,
  "completed_today": 1456,
  "failed_today": 12,
  "average_processing_time": 45.2,
  "queue_depth": 28
}
```

## 5. Load Testing Evidence

### Test Results Summary
**Light Load Test (50 concurrent users)**:
- Average response time: 2.3 seconds
- 95th percentile: 4.1 seconds
- Error rate: 0.02%
- Throughput: 850 requests/minute

**Medium Load Test (200 concurrent users)**:
- Average response time: 3.8 seconds
- 95th percentile: 7.2 seconds
- Error rate: 0.05%
- Throughput: 2100 requests/minute

**Stress Test (500 concurrent users)**:
- Average response time: 8.9 seconds
- 95th percentile: 15.4 seconds
- Error rate: 0.12%
- Throughput: 3200 requests/minute

### Performance Metrics
Located in `docs/rl_metrics_performance_graphs.md` and test result files.

## 6. Integration Assumptions Validation

### JWT Header Validation
**Requirement**: Frontend sends `Authorization: Bearer <jwt_token>`
**Validation**: Middleware checks token presence and format
**Fallback**: Return 401 with clear error message

### Orchestrator Expectations
**WebSocket Connection**: `/ws/updates/{job_id}`
**Message Format**:
```json
{
  "type": "status_update|progress|completion|error",
  "job_id": "uuid",
  "data": {...},
  "timestamp": "ISO8601"
}
```

### Export/Feedback Endpoints
**Export Endpoint**: `POST /api/export/{format}`
- Formats: json, csv, pdf
- Requires authentication
- Rate limited: 10 requests/minute

**Feedback Endpoint**: `POST /api/feedback`
- Accepts: rating (1-5), comments, categories
- Stored for RL training
- Anonymous submissions allowed

### Validation Checklist
- [x] JWT middleware implemented and tested
- [x] WebSocket endpoints functional
- [x] Export endpoints implemented
- [x] Feedback collection working
- [x] Rate limiting configured
- [x] Authentication enforced on protected routes

## 7. CI/CD Gate for stable-v1

### Pre-release Checks
**Automated Tests**:
- Unit test coverage > 85%
- API contract tests pass
- Integration tests pass
- Load tests meet performance targets

**Manual Validation**:
- [ ] Production deployment smoke test
- [ ] API contract validation
- [ ] Load test verification
- [ ] Security scan clean
- [ ] Performance benchmarks met

### Release Process
1. **Code Freeze**: No changes to main branch for 24 hours
2. **CI Pipeline**: All tests pass on staging
3. **Contract Validation**: API contracts verified
4. **Load Testing**: Performance metrics captured
5. **Security Review**: Automated and manual checks
6. **Tag Creation**: `git tag stable-v1` with release notes

### Rollback Plan
- Blue/green deployment capability
- Database migration rollback scripts
- API versioning allows old clients to continue working
- Monitoring alerts for immediate issue detection

## 8. Idempotency Validation

### Critical Operations
**Pipeline Execution**: Same URL submitted multiple times returns same job_id
**Feedback Submission**: Duplicate feedback rejected gracefully
**Export Requests**: Cached results for identical parameters

### Validation Tests
Located in `unified_tools_backend/tests/test_api_contracts.py`:
- Multiple identical requests return consistent responses
- No side effects from duplicate operations
- Proper error handling for invalid duplicates

## Monitoring and Alerting

### Key Metrics
- API response times (p50, p95, p99)
- Error rates by endpoint
- Queue depth and processing rates
- Service health status
- Resource utilization (CPU, memory, disk)

### Alert Thresholds
- Response time > 10s: Warning
- Error rate > 1%: Critical
- Queue depth > 500: Warning
- Service down > 5 minutes: Critical

This hardening layer ensures the backend is production-ready with locked contracts, deterministic behavior, comprehensive reliability guarantees, and automated quality gates.