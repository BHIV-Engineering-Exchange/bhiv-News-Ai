# Samachar — Vision Runtime — SVACS Interface Contract

## Contract Version

`1.0.0`

## Contract Status

Frozen for current integration handover.

---

# Integration Boundary

```text
Input Sources
     ↓
Samachar
     ↓
Vision Runtime when image processing is required
     ↓
Samachar Canonical Intelligence
     ↓
SVACS v1 Structured Intelligence
     ↓
SVACS
```

---

# 1. Samachar to Vision Runtime

## Endpoint

`POST /api/v1/analyze`

## Ownership

Vision Runtime owner: Vijay Dhawan

Samachar consumes this runtime as an external service.

## Input

Image content supplied by Samachar through the agreed runtime request
interface.

Samachar does not perform vision processing before classification.

## Expected Response

```json
{
  "replay_id": "uuid",
  "detections": [
    {
      "label": "Vessel",
      "confidence": 0.89,
      "bounding_box": {
        "x_min": 10.5,
        "y_min": 20.0,
        "x_max": 150.5,
        "y_max": 200.0
      }
    }
  ],
  "ocr_results": [
    {
      "text": "IMO 1234567",
      "confidence": 0.95,
      "bounding_box": {
        "x_min": 50.0,
        "y_min": 80.0,
        "x_max": 120.0,
        "y_max": 100.0
      }
    }
  ],
  "explainable_image_base64": null
}
```

## Vision Runtime Fields

| Field | Type | Description |
|---|---|---|
| `replay_id` | string | Vision Runtime execution identifier |
| `detections` | array | Visual detection results |
| `detections[].label` | string | Detection label |
| `detections[].confidence` | number | Detection confidence |
| `detections[].bounding_box` | object | Detection coordinates |
| `ocr_results` | array | OCR observations |
| `ocr_results[].text` | string | OCR text |
| `ocr_results[].confidence` | number | OCR confidence |
| `ocr_results[].bounding_box` | object | OCR coordinates |
| `explainable_image_base64` | string/null | Optional explainable image |

## Trace Rule

The Vision Runtime `replay_id` must not replace the Samachar `trace_id`.

Samachar preserves it as:

`provenance.vision_replay_id`

---

# 2. Samachar Canonical Intelligence

## Samachar Trace Identifier

Format:

`SAM-<uuid4>`

Example:

`SAM-b95e810c-5503-48c6-9490-ad1de6eb4aa9`

The Samachar trace ID identifies the governed ingestion lineage.

## Canonical Governance Fields

Required governance fields include:

- `schema_version`
- `trace_id`
- `timestamp`
- `source`
- `provenance`
- `processing_trace`
- `downstream`
- `errors`

## Provenance Contract

```json
{
  "origin": "operator_image",
  "processed_by": [
    "samachar",
    "vision_runtime"
  ],
  "vision_runtime_invoked": true,
  "vision_replay_id": "external-replay-id"
}
```

Manual and satellite deterministic inputs may additionally contain:

`input_fingerprint`

---

# 3. Samachar to SVACS

## SVACS v1 Structured Intelligence Contract

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

## Field Mapping

| SVACS Field | Samachar / Vision Source |
|---|---|
| `trace_id` | Samachar canonical `trace_id` |
| `source_type` | `source.input_type` |
| `vessel_class` | Vision detection label mapped to SVACS taxonomy |
| `confidence_score` | Normalized Samachar confidence |
| `vision_confidence` | Primary Vision Runtime detection confidence |
| `visual_features` | Upstream supported visual features |
| `dimensions_estimate` | Upstream supported dimensions |
| `ais_data.mmsi` | Supported maritime identifier mapping |
| `ais_data.speed_knots` | Upstream AIS source when available |
| `timestamp_utc` | Canonical Samachar timestamp |

## Approved Vessel Taxonomy

- `cargo`
- `tanker`
- `patrol`
- `fishing`
- `submarine`
- `unknown`

Unsupported or generic labels map to:

`unknown`

Samachar does not perform maritime reasoning to infer a more specific
class.

---

# 4. Compatibility Guarantees

For contract version `1.0.0`:

1. Samachar generates and preserves `SAM-*` trace identifiers.
2. Vision Runtime replay IDs remain provenance identifiers.
3. SVACS vessel classes remain inside the approved v1 taxonomy.
4. Confidence values exposed to SVACS remain in the range `0.0` to `1.0`.
5. Runtime timestamps use ISO-8601.
6. Unknown intelligence is not fabricated.
7. External dependency failures are not marked ready for downstream processing.
8. Satellite image processing is not assumed until a production feed contract exists.

---

# 5. Error Contract

Governed runtime failures contain:

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
    "code": "ERROR_CODE",
    "message": "Failure description",
    "stage": "processing_stage"
  },
  "processing_trace": {
    "status": "FAILED",
    "failed_step": "Processing Step"
  },
  "downstream": {
    "target_system": "svacs",
    "ready_for_processing": false
  }
}
```

Failed governed intelligence must not be treated as successful SVACS
input.

---

# Ownership Boundaries

## Samachar

Owns ingestion, orchestration, canonical mapping, traceability,
provenance, replay continuity, and contract compatibility.

## Vision Runtime

Owns image processing, object detection, OCR, and visual detection
confidence.

## SVACS

Owns maritime reasoning, vessel intelligence, Jane's intelligence,
sensor fusion, and operational analysis.