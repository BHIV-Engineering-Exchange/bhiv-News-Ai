# Reliability Guide for News AI Backend

## Overview

This guide documents the reliability mechanisms, retry rules, failure modes, and fallback order for the News AI Backend. It ensures consistent and predictable system behavior under various conditions.

## Reliability Architecture

The system implements multiple layers of reliability:

1. **Request Validation** - Input validation and sanitization
2. **Service Fallbacks** - Graceful degradation when services unavailable
3. **Retry Logic** - Exponential backoff for transient failures
4. **Circuit Breakers** - Prevent cascade failures
5. **Monitoring** - Comprehensive health checks and metrics

## Retry Rules and Policies

### External API Retries

#### Uniguru AI Service
- **Max Retries**: 3 attempts
- **Backoff Strategy**: Exponential (1s, 2s, 4s)
- **Retry Conditions**:
  - HTTP 5xx errors
  - Connection timeouts
  - Rate limit exceeded (429)
- **No Retry Conditions**:
  - HTTP 4xx errors (except 429)
  - Authentication failures
  - Invalid request data

#### BHIV Core Integration
- **Max Retries**: 5 attempts
- **Backoff Strategy**: Exponential (2s, 4s, 8s, 16s, 32s)
- **Retry Conditions**:
  - Connection failures
  - WebSocket disconnections
  - Push timeouts
- **Circuit Breaker**: Opens after 10 consecutive failures

### Database Operations
- **Max Retries**: 3 attempts
- **Backoff Strategy**: Linear (0.5s, 1s, 1.5s)
- **Retry Conditions**:
  - Connection timeouts
  - Temporary unavailability
  - Lock conflicts

### Queue Operations
- **Max Retries**: 2 attempts
- **Backoff Strategy**: Fixed (1s)
- **Retry Conditions**:
  - Queue full
  - Worker unavailable

## Failure Modes and Recovery

### Service Unavailable Scenarios

#### Uniguru AI Down
**Detection**: Health check fails or API returns 5xx
**Fallback**: Use cached responses or skip AI processing
**Recovery**: Automatic when service returns 200
**Impact**: Reduced AI features, basic processing continues

#### BHIV Core Down
**Detection**: WebSocket connection fails or push returns error
**Fallback**: Queue failed pushes for retry, disable real-time features
**Recovery**: Automatic reconnection with exponential backoff
**Impact**: Delayed content delivery, offline mode

#### Database Down
**Detection**: Connection timeout or query failures
**Fallback**: Read-only mode, cache writes locally
**Recovery**: Automatic reconnection
**Impact**: No new data persistence, read operations fail

#### Queue Worker Down
**Detection**: Job submission timeouts or queue depth > threshold
**Fallback**: Synchronous processing (limited throughput)
**Recovery**: Worker restart or scaling
**Impact**: Reduced throughput, potential delays

### Data Consistency Failures

#### Partial Pipeline Failures
**Detection**: Component fails mid-pipeline
**Recovery**: Rollback to last good state, retry from checkpoint
**Fallback**: Mark as partial success, allow manual correction

#### RL Feedback Inconsistencies
**Detection**: Feedback calculation produces invalid scores
**Recovery**: Use default thresholds, log for analysis
**Fallback**: Skip quality gating, allow all content

## Fallback Order and Priority

### Primary Processing Path
1. **News Extraction** → **Script Generation** → **RL Feedback** → **BHIV Push**
2. If any step fails, attempt fallback processing

### Fallback Processing Order

#### Step 1: News Extraction Fails
1. Use cached news data (if available)
2. Skip to script generation with minimal data
3. Mark as degraded quality

#### Step 2: Script Generation Fails
1. Use template-based script generation
2. Skip AI enhancement features
3. Use basic prompt structure

#### Step 3: RL Feedback Fails
1. Apply default quality thresholds
2. Skip correction logic
3. Allow content with warning

#### Step 4: BHIV Push Fails
1. Queue for later retry
2. Store locally for manual push
3. Notify administrators

### Service-Level Fallbacks

#### Uniguru AI Fallbacks
1. **Primary**: Direct API call
2. **Fallback 1**: Cached results (if < 1 hour old)
3. **Fallback 2**: Rule-based processing
4. **Fallback 3**: Skip AI features

#### BHIV Integration Fallbacks
1. **Primary**: Real-time WebSocket push
2. **Fallback 1**: HTTP API push
3. **Fallback 2**: Queue for batch processing
4. **Fallback 3**: Local storage only

## Error Classification

### Transient Errors (Retry)
- Network timeouts
- Service temporarily unavailable (5xx)
- Rate limiting (429)
- Connection pooling issues

### Permanent Errors (No Retry)
- Authentication failures (401/403)
- Invalid request data (400)
- Not found (404)
- Client errors (4xx except 429)

### Circuit Breaker Conditions
- **Failure Threshold**: 10 consecutive failures
- **Recovery Timeout**: 60 seconds
- **Success Threshold**: 3 consecutive successes

## Monitoring and Alerting

### Health Check Endpoints
- `/health` - Overall system health
- `/api/bhiv/status` - BHIV connectivity
- Individual service health checks

### Key Metrics to Monitor
- **Error Rates**: >5% triggers warning, >15% critical
- **Response Times**: >30s triggers warning, >60s critical
- **Queue Depth**: >100 pending jobs triggers warning
- **Circuit Breaker State**: Open state triggers alert

### Alert Conditions
- Service unavailable for >5 minutes
- Error rate >10% for >10 minutes
- Queue depth >500 jobs
- Database connection failures >3 in 5 minutes

## Operational Procedures

### Manual Recovery Steps

#### Service Restart
1. Check health endpoint for specific failures
2. Restart affected service
3. Verify health checks pass
4. Monitor error rates for 15 minutes

#### Database Recovery
1. Check database connectivity
2. Verify replica set status
3. Restore from backup if needed
4. Validate data consistency

#### Queue Recovery
1. Check queue worker processes
2. Restart failed workers
3. Monitor queue processing rate
4. Clear stuck jobs if necessary

### Maintenance Windows
- **Preferred Time**: 02:00-04:00 UTC (low traffic)
- **Duration**: < 30 minutes
- **Notification**: 24 hours advance notice
- **Rollback Plan**: Immediate service restart

## Performance Degradation Handling

### Graduated Degradation Levels

#### Level 1: Minor Issues (<5% impact)
- Log warnings
- Continue normal operation
- Monitor for escalation

#### Level 2: Moderate Issues (5-15% impact)
- Enable additional logging
- Reduce non-critical features
- Alert on-call engineer

#### Level 3: Major Issues (15-50% impact)
- Enable fallback modes
- Reduce throughput
- Page on-call team

#### Level 4: Critical Issues (>50% impact)
- Emergency protocols
- Service degradation notices
- Full incident response

## Testing Reliability

### Chaos Engineering Tests
- Random service failures
- Network partition simulation
- Resource exhaustion tests
- Database failover tests

### Load Testing with Failures
- Inject failures during load tests
- Verify fallback performance
- Test recovery under load

### Integration Testing
- Full pipeline with service failures
- End-to-end with network issues
- Recovery time measurement

## Version History

- **v1.0.0**: Initial reliability framework
- **Schema Frozen**: Yes (for stable-v1 release)