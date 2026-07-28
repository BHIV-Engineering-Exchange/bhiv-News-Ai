# API Samples

This document contains representative API request and response samples collected during production validation of the Samachar / Guptachar Production Gateway Convergence (Phase IV).

---

# 1. Manual Intelligence

## Endpoint

POST /api/v1/intelligence/manual

## Sample Request

```json
{
  "content": "Suspicious vessel detected near the western coastline. Local authorities have initiated surveillance.",
  "source": "operator"
}
```

## Sample Response

```json
{
  "schema_version": "1.0.0",
  "trace_id": "SAM-9a0f5d38-0d1c-4a91-bf85-0f94c3dcb91f",
  "timestamp": "2026-07-24T09:15:21.624Z",
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
    "vision_runtime_invoked": false
  },
  "intelligence": {
    "...": "classified intelligence output"
  },
  "replay": {
    "status": "MISS"
  },
  "errors": []
}
```

---

# 2. Image Intelligence

## Endpoint

POST /api/v1/intelligence/image

Content-Type:

multipart/form-data

## Sample Request

```text
image = cargo_ship.jpg
```

## Sample Response

```json
{
  "trace_id": "SAM-89a008b8-2ae3-4c94-9952-00f97891cdb7",
  "source_type": "image",
  "vessel_class": "cargo",
  "confidence_score": 0,
  "vision_confidence": 0.6466519236564636,
  "ocr_results": [
    {
      "text": "VORWEGIAN JADE",
      "confidence": 0.3227226253707913
    }
  ],
  "visual_features": [],
  "dimensions_estimate": {
    "length_m": null,
    "beam_m": null
  },
  "ais_data": {
    "mmsi": null,
    "speed_knots": null
  },
  "timestamp_utc": "2026-07-17T05:19:39.732412+00:00"
}
```

---

# 3. Replay MISS Validation

## Request

POST /api/v1/intelligence/image

Upload:

```text
cargo_ship.jpg
```

## Result

The uploaded image was processed by the live Vision Runtime.

ReplayStore did not contain a matching fingerprint.

Vision Runtime was invoked.

The canonical response was persisted.

## Replay Section

```json
{
  "replay": {
    "status": "MISS",
    "input_fingerprint": "sha256:96dd36...",
    "original_trace_id": "SAM-758f80eb-f0b7-4d67-95af-bfcf48fae519"
  }
}
```

---

# 4. Replay HIT Validation

## Request

POST /api/v1/intelligence/image

Upload the same image again:

```text
cargo_ship.jpg
```

## Result

ReplayStore located an existing fingerprint.

The cached canonical intelligence was returned.

Vision Runtime invocation was skipped.

## Replay Section

```json
{
  "replay": {
    "status": "HIT",
    "input_fingerprint": "sha256:96dd36...",
    "original_trace_id": "SAM-758f80eb-f0b7-4d67-95af-bfcf48fae519"
  }
}
```

---

# Validation Summary

| Validation | Status |
|------------|--------|
| Manual Intelligence | PASS |
| Image Intelligence | PASS |
| Replay MISS | PASS |
| Replay HIT | PASS |
| Canonical Response | PASS |
| Trace ID Propagation | PASS |
| Execution ID Propagation | PASS |
| Vision Runtime Replay ID | PASS |
| Contract Validation | PASS |
| SVACS Compatibility | PASS |

---

# Conclusion

The collected API samples confirm successful production execution across manual and image intelligence ingestion. Canonical request and response contracts remained stable, replay behaviour was deterministic, execution context was preserved, and downstream compatibility with SVACS was successfully validated.