# Samachar → Vision Runtime → SVACS Integration Code Packet

## Review Scope

This code packet identifies the primary files involved in the Samachar Intelligence Integration Runtime.

The implementation establishes Samachar as the governed upstream intelligence ingestion and orchestration layer for SVACS.

The integration supports:

- Manual intelligence ingestion
- Image intelligence ingestion
- Vision Runtime invocation
- Satellite feed ingestion interface
- Canonical intelligence generation
- SVACS contract mapping
- Replay-safe processing
- Processing trace and provenance
- Governed runtime error responses
- Versioned contract validation

---

## Primary Review Files

### 1. `main.py`

Review the versioned intelligence API endpoints:

- `POST /api/v1/intelligence/image`
- `POST /api/v1/intelligence/manual`
- `POST /api/v1/intelligence/satellite`

Approximate endpoint locations:

- Image ingestion: around line 6894
- Manual ingestion: around line 7150
- Satellite ingestion: around line 7217

Responsibilities:

- API input handling
- Request validation
- Service orchestration
- Governed error handling
- Runtime response publication

---

### 2. `analysis/vision_runtime_client.py`

Responsibility:

Vision Runtime API client.

Flow:

Image bytes
→ Vision Runtime request
→ Response validation
→ Vision intelligence response

The client consumes the external Vision Runtime.

It does not perform:

- Image preprocessing
- Object detection
- OCR
- Vessel detection
- Vision classification

These capabilities remain owned by the Vision Runtime.

---

### 3. `analysis/vision_intelligence_service.py`

Responsibility:

Image intelligence orchestration.

Flow:

Image ingestion
→ Vision Runtime
→ OCR normalization
→ Samachar intelligence processing
→ Canonical mapping

Generates:

- Samachar trace ID
- Source metadata
- Provenance
- Vision intelligence
- Samachar intelligence
- Processing trace
- Downstream readiness state

---

### 4. `analysis/manual_intelligence_service.py`

Responsibility:

Manual operator intelligence ingestion.

Flow:

Operator content
→ Input validation
→ Deterministic fingerprint generation
→ Replay lookup
→ Samachar intelligence processing
→ Canonical intelligence

Supports replay-safe processing through deterministic SHA-256 input fingerprints.

---

### 5. `analysis/satellite_intelligence_service.py`

Responsibility:

Future satellite feed ingestion interface.

The current implementation accepts:

- Feed ID
- Source timestamp
- Image reference
- Feed metadata

The service does not perform satellite image processing.

Current integration status:

- Feed interface: AVAILABLE
- Vision processing: NOT_INVOKED
- Production feed adapter: PENDING_CONTRACT

The production satellite feed adapter can be connected when the upstream feed contract is finalized.

---

### 6. `analysis/svacs_intelligence_mapper.py`

Responsibility:

Maps Samachar canonical intelligence into the SVACS v1 structured intelligence contract.

The mapper performs schema translation only.

It does not perform:

- Maritime reasoning
- Vessel detection
- Dimension estimation
- Sensor fusion
- Vessel intelligence enrichment

Primary mapping responsibilities:

- Preserve Samachar trace ID
- Map source type
- Map Vision Runtime labels to the approved SVACS vessel taxonomy
- Preserve Vision Runtime confidence
- Map Samachar confidence into the SVACS confidence range
- Extract supported maritime identifiers from OCR
- Generate the SVACS v1 payload structure

---

### 7. `runtime/replay_store.py`

Responsibility:

In-memory replay continuity store.

Supports:

- Deterministic fingerprint lookup
- Replay MISS detection
- Canonical result storage
- Replay HIT detection
- Original trace ID preservation

Replay behavior:

Same input
→ Same fingerprint
→ Existing canonical result reused
→ Original trace ID preserved

---

### 8. Governed Runtime Error Response

Review the runtime error response implementation used by the image intelligence endpoint.

The governed failure model preserves:

- Schema version
- Trace ID
- Failure timestamp
- Source type
- Error code
- Error message
- Failure stage
- Failed processing step
- Downstream readiness state

When the Vision Runtime is unavailable or returns an HTTP error:

`downstream.ready_for_processing = false`

Samachar does not publish failed image intelligence as valid SVACS intelligence.

---

### 9. `contracts/`

Review the SVACS contract and validation implementation.

Responsibilities:

- Versioned SVACS v1 contract
- Vessel taxonomy validation
- Confidence range validation
- Samachar trace ID validation
- ISO-8601 timestamp validation
- Contract compatibility checks

---

## Primary Integration Tests

### `tests/test_samachar_svacs_integration.py`

Primary end-to-end integration proof.

Validates:

1. Manual intelligence ingestion
2. Satellite feed ingestion
3. Samachar canonical intelligence to SVACS mapping
4. SVACS v1 contract validation

Expected result:

`3 passed`

---

### `tests/test_svacs_contract_validator.py`

Validates both:

- Valid SVACS v1 payload acceptance
- Invalid payload rejection

Expected result:

`2 passed`

---

### `tests/test_replay_store.py`

Validates replay store behavior.

Expected result:

`1 passed`

---

### `tests/test_manual_intelligence_service.py`

Demonstrates:

First execution → Replay MISS

Second identical execution → Replay HIT

The original Samachar trace ID is preserved.

---

### `tests/test_error_response.py`

Validates governed runtime failure responses.

Demonstrates that Vision Runtime failures are:

- Classified
- Traceable
- Stage-aware
- Blocked from downstream processing

---

## Integration Boundary

### Samachar Owns

- Manual intelligence ingestion
- Image ingestion
- Satellite feed interface
- Vision Runtime invocation
- API orchestration
- Canonical intelligence generation
- Trace IDs
- Processing trace
- Provenance
- Replay continuity
- Contract mapping
- Runtime observability

### Vision Runtime Owns

- Image processing
- Object detection
- OCR
- Vision detection confidence

### SVACS Owns

- Maritime reasoning
- Vessel intelligence
- Jane's intelligence
- Sensor fusion
- Operational maritime analysis

---

## Reviewer Recommendation

For the fastest review path, inspect files in this order:

1. `tests/test_samachar_svacs_integration.py`
2. `analysis/vision_intelligence_service.py`
3. `analysis/vision_runtime_client.py`
4. `analysis/svacs_intelligence_mapper.py`
5. `analysis/manual_intelligence_service.py`
6. `analysis/satellite_intelligence_service.py`
7. `runtime/replay_store.py`
8. `contracts/`
9. Intelligence endpoints in `main.py`

This review path demonstrates the complete integration architecture without requiring exploration of the full News-AI repository.