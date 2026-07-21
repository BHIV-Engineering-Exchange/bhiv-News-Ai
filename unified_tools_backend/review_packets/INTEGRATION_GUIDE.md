# Samachar Intelligence Integration Guide

## Purpose

This guide explains how to run and validate the Samachar Intelligence
Integration Runtime.

---

# 1. Runtime Configuration

Configure the external Vision Runtime URL:

```env
VISION_RUNTIME_URL=<vision-runtime-base-url>
```

The Vision Runtime must expose:

`POST /api/v1/analyze`

Do not append `/api/v1/analyze` to `VISION_RUNTIME_URL`.

The Samachar Vision Runtime client appends the endpoint path during
invocation.

---

# 2. Start the Runtime

From:

`unified_tools_backend/`

activate the Python environment.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn main:app --reload
```

The local runtime is available at:

`http://127.0.0.1:8000`

Swagger documentation:

`http://127.0.0.1:8000/docs`

---

# 3. Validate Manual Ingestion

Use:

`POST /api/v1/intelligence/manual`

Example:

```json
{
  "content": "A suspected patrol vessel was observed near Mumbai coastal waters. Authorities started an investigation.",
  "source": "operator"
}
```

Confirm:

- `schema_version = 1.0.0`
- `trace_id` begins with `SAM-`
- `source.input_type = manual`
- `provenance.origin = operator_manual`
- `downstream.target_system = svacs`
- `downstream.ready_for_processing = true`

---

# 4. Validate Replay Continuity

Run:

```powershell
python -m pytest tests/test_manual_intelligence_service.py -s
```

Expected behavior:

```text
FIRST MANUAL EXECUTION
replay.status = MISS

SECOND MANUAL EXECUTION
replay.status = HIT
```

The second execution must preserve the original trace ID.

---

# 5. Validate Satellite Feed Interface

Use:

`POST /api/v1/intelligence/satellite`

Example:

```json
{
  "feed_id": "SAT-DEMO-001",
  "timestamp_utc": "2026-07-15T06:00:00+00:00",
  "image_reference": "satellite://feed/image/demo-001",
  "metadata": {
    "provider": "integration_demo",
    "region": "arabian_sea"
  }
}
```

Confirm:

```text
feed_interface = AVAILABLE
vision_processing = NOT_INVOKED
production_feed_adapter = PENDING_CONTRACT
```

---

# 6. Validate Image Intelligence

Use:

`POST /api/v1/intelligence/image`

Upload a JPEG, PNG, or WEBP image.

Expected runtime flow:

```text
Image
  ↓
Samachar
  ↓
Vision Runtime
  ↓
Canonical Intelligence
  ↓
SVACS Mapper
  ↓
SVACS v1 Payload
```

If the Vision Runtime is unavailable, confirm that the response contains:

```text
status = FAILED
processing_trace.status = FAILED
downstream.ready_for_processing = false
```

---

# 7. Validate SVACS Contract

Run:

```powershell
python -m pytest tests/test_svacs_contract_validator.py -s
```

Expected:

```text
2 passed
```

A valid payload should report:

```json
{
  "valid": true,
  "contract_version": "1.0.0",
  "errors": []
}
```

---

# 8. Run Integration Tests

Run:

```powershell
python -m pytest tests/test_samachar_svacs_integration.py -s
```

Expected:

```text
3 passed
```

The suite validates:

- Manual intelligence integration
- Satellite feed integration
- Samachar to SVACS contract mapping
- SVACS v1 contract validation

---

# 9. Validate Governed Errors

Run:

```powershell
python -m pytest tests/test_error_response.py -s
```

Expected:

```text
1 passed
```

Confirm that failed intelligence contains:

```text
error.code
error.stage
processing_trace.failed_step
downstream.ready_for_processing = false
```

---

# 10. Known Limitations

- Image intelligence depends on the externally hosted Vision Runtime.
- External tunnel or runtime URL changes can affect live image tests.
- Samachar does not perform satellite image processing.
- Samachar does not estimate vessel dimensions.
- Maritime reasoning remains owned by SVACS.
- Replay storage is currently runtime-local.

---

# Review Artifacts

See:

- `REVIEW_PACKET.md`
- `review_focus.md`
- `API_DOCUMENTATION.md`
- `INTERFACE_CONTRACT.md`
- `code_packets/SAMACHAR_SVACS_CODE_PACKET.md`
- `screenshots/`