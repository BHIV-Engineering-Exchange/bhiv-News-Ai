# Samachar Intelligence Runtime — API Documentation

## API Version

`v1`

## Runtime Purpose

The Samachar Intelligence Runtime exposes versioned ingestion APIs for
manual intelligence, image intelligence, and future satellite feed
integration.

Samachar acts as the governed upstream intelligence ingestion and
orchestration layer for SVACS.

---

# 1. Manual Intelligence Ingestion

## Endpoint

`POST /api/v1/intelligence/manual`

## Purpose

Accept manual intelligence submitted by an operator and convert it into
a canonical Samachar intelligence envelope.

## Request

Content-Type:

`application/json`

Example:

```json
{
  "content": "A suspected patrol vessel was observed near Mumbai coastal waters. Authorities started an investigation.",
  "source": "operator"
}
```

## Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | string | Yes | Manual intelligence content |
| `source` | string | No | Source or submitting operator identifier |

## Processing Flow

```text
Manual Input
     ↓
Input Validation
     ↓
Deterministic Fingerprint
     ↓
Replay Lookup
     ↓
Samachar Intelligence Processing
     ↓
Canonical Intelligence
```

## Response

The response contains:

- `schema_version`
- `trace_id`
- `timestamp`
- `source`
- `provenance`
- `intelligence`
- `processing_trace`
- `downstream`
- `replay`
- `errors`

Example structure:

```json
{
  "schema_version": "1.0.0",
  "trace_id": "SAM-<uuid>",
  "timestamp": "ISO-8601",
  "source": {
    "input_type": "manual",
    "source_system": "samachar",
    "submitted_by": "operator"
  },
  "provenance": {
    "origin": "operator_manual",
    "processed_by": [
      "samachar"
    ],
    "vision_runtime_invoked": false,
    "vision_replay_id": null,
    "input_fingerprint": "sha256:<fingerprint>"
  },
  "intelligence": {},
  "processing_trace": {
    "status": "SUCCESS",
    "steps": [
      "Manual Ingestion",
      "Samachar Intelligence",
      "Canonical Mapping"
    ]
  },
  "downstream": {
    "target_system": "svacs",
    "ready_for_processing": true
  },
  "replay": {
    "status": "MISS",
    "input_fingerprint": "sha256:<fingerprint>",
    "original_trace_id": "SAM-<uuid>"
  },
  "errors": []
}
```

---

# 2. Image Intelligence Ingestion

## Endpoint

`POST /api/v1/intelligence/image`

## Purpose

Accept an operator image, invoke the external Vision Runtime, create
canonical intelligence, and map the result into the SVACS v1 structured
intelligence contract.

## Request

Content-Type:

`multipart/form-data`

## Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `image` | binary file | Yes | JPEG, PNG, or WEBP image |

Supported media types:

- `image/jpeg`
- `image/png`

## Processing Flow

```text
Image Upload
     ↓
Image Validation
     ↓
Vision Runtime Invocation
     ↓
Vision Response Validation
     ↓
OCR Normalization
     ↓
Canonical Intelligence
     ↓
SVACS Contract Mapping
```

## Successful Response

The endpoint returns the SVACS v1 structured intelligence payload.

```json
{
  "trace_id": "SAM-<uuid>",
  "source_type": "image",
  "vessel_class": "unknown",
  "confidence_score": 0.0,
  "vision_confidence": 0.89,
  "visual_features": [],
  "dimensions_estimate": {
    "length_m": null,
    "beam_m": null
  },
  "ais_data": {
    "mmsi": null,
    "speed_knots": null
  },
  "timestamp_utc": "ISO-8601"
}
```

## Governed Failure Response

If the external Vision Runtime is unavailable or fails, Samachar returns
a governed failure envelope.

```json
{
  "schema_version": "1.0.0",
  "trace_id": "SAM-<uuid>",
  "timestamp": "ISO-8601",
  "status": "FAILED",
  "source": {
    "input_type": "image",
    "source_system": "samachar"
  },
  "error": {
    "code": "VISION_RUNTIME_HTTP_ERROR",
    "message": "Vision Runtime returned HTTP 404",
    "stage": "vision_runtime"
  },
  "processing_trace": {
    "status": "FAILED",
    "failed_step": "Vision Runtime"
  },
  "downstream": {
    "target_system": "svacs",
    "ready_for_processing": false
  }
}
```

## Governed Error Codes

- `VISION_RUNTIME_UNAVAILABLE`
- `VISION_RUNTIME_TIMEOUT`
- `VISION_RUNTIME_HTTP_ERROR`
- `VISION_RUNTIME_PROCESSING_FAILED`
- `INVALID_IMAGE_INPUT`
- `IMAGE_INTELLIGENCE_FAILED`

---

# 3. Satellite Feed Ingestion

## Endpoint

`POST /api/v1/intelligence/satellite`

## Purpose

Provide a governed future satellite feed ingestion interface.

The endpoint does not perform satellite image processing.

## Request

Content-Type:

`application/json`

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

## Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `feed_id` | string | Yes | Satellite feed identifier |
| `timestamp_utc` | string | Yes | ISO-8601 source timestamp with timezone |
| `image_reference` | string/null | No | External feed image reference |
| `metadata` | object | No | Feed-specific metadata |

## Processing Flow

```text
Satellite Feed
      ↓
Feed Validation
      ↓
Timestamp Validation
      ↓
Deterministic Fingerprint
      ↓
Replay Lookup
      ↓
Provenance Capture
      ↓
Canonical Feed Envelope
```

## Integration Status

```json
{
  "feed_interface": "AVAILABLE",
  "vision_processing": "NOT_INVOKED",
  "production_feed_adapter": "PENDING_CONTRACT"
}
```

The production satellite adapter can be integrated after the upstream
feed contract is finalized.

---

# Health and Existing Runtime Documentation

The FastAPI application exposes interactive OpenAPI documentation
through the runtime Swagger interface.

Local development documentation:

`/docs`

OpenAPI schema:

`/openapi.json`

---

# External Runtime Configuration

Image intelligence requires:

`VISION_RUNTIME_URL`

The configured Vision Runtime must expose:

`POST /api/v1/analyze`

Vision Runtime availability is an external integration dependency.