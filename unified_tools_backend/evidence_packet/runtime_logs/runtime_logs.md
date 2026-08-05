# Replay Validation Runtime Logs

## First Execution (Replay MISS)

---

## Successful Runtime Events

- Image received successfully
- Vision Runtime invoked
- OCR completed
- Canonical intelligence generated
- Replay fingerprint calculated
- Replay validation executed
- SVACS contract validated
- Bucket artifact stored successfully

---

### Request (Replay MISS)

#### Endpoint

```http
POST /api/v1/intelligence/image
```

#### Input

```text
cargo_ship.jpg
```

### Runtime Output

```text
[Replay] Fingerprint:
sha256:cf1bcaf2dd58678be77f50073e0656ea56546799248d1dfd04c625b86ed1184a

Replay Status:
MISS

Vision Runtime:
Calling live Vision Runtime...

ReplayStore:
Saving canonical response...
```

### Replay Information

```json
{
  "status": "MISS",
  "input_fingerprint": "sha256:cf1bcaf2dd58678be77f50073e0656ea56546799248d1dfd04c625b86ed1184a",
  "original_trace_id": "SAM-09f3a454-e930-4b4c-a1e8-68db52c316bd"
}
```

### Processing Trace

```json
{
  "status": "SUCCESS",
  "execution_id": "EXEC-26882133-48c8-410e-8e8d-95c509bb154b",
  "trace_id": "SAM-09f3a454-e930-4b4c-a1e8-68db52c316bd",
  "vision_replay_id": "e9238349-9b68-4318-afc2-1168785522d1",
  "steps": [
    {
      "name": "Image Ingestion",
      "status": "SUCCESS"
    },
    {
      "name": "Vision Runtime",
      "status": "SUCCESS"
    },
    {
      "name": "OCR Normalization",
      "status": "SUCCESS"
    },
    {
      "name": "Samachar Intelligence",
      "status": "SUCCESS"
    },
    {
      "name": "Canonical Mapping",
      "status": "SUCCESS"
    }
  ],
  "processing_time": {
    "vision_runtime": 10.945,
    "ocr_normalization": 0.001,
    "intelligence_processing": 0.072,
    "canonical_mapping": 0.000,
    "total": 11.024
  }
}
```

### Contract Validation

```text
SVACS IMAGE ENDPOINT
--------------------
Contract Validation : PASSED

Trace ID           : SAM-09f3a454-e930-4b4c-a1e8-68db52c316bd
Contract Version   : 1.0.0

HTTP Response      : 200 OK
```

---

## Second Execution (Replay HIT)

### Request (Replay HIT)

```http
POST /api/v1/intelligence/image

(Same image uploaded again.)

### Runtime Output (Replay HIT)

```text
[Replay] Fingerprint:
sha256:cf1bcaf2dd58678be77f50073e0656ea56546799248d1dfd04c625b86ed1184a

Replay Status:
HIT

Vision Runtime:
Skipped (cached replay used)
```

### Replay Information (Replay HIT)

```json
{
  "status": "HIT",
  "input_fingerprint": "sha256:cf1bcaf2dd58678be77f50073e0656ea56546799248d1dfd04c625b86ed1184a",
  "original_trace_id": "SAM-09f3a454-e930-4b4c-a1e8-68db52c316bd"
}
```

### Bucket

```text
========== BUCKET ==========
{'success': True, 'artifact_id': '9d018606-42ee-4f31-9b4c-0e4872a43c53', 'hash': '1d77aaf3dc32c38008b0993abd02e3e2079507b2f0f19f9638af84963a68fd5e', 'parent_hash': '2bdc81f2450675581befed4ae644078065e4e4e0f9dd93094ce07a2b6c49749a', 'timestamp': '2026-08-04T09:51:35.135586+00:00', 'storage_type': 'append_only', 'message': 'Artifact stored successfully in append-only log'}
```

---

## Example Runtime Sequence

```text
Image Uploaded
↓

Vision Runtime Invoked

↓

OCR Normalized

↓

Canonical Intelligence Generated

↓

Replay Validated

↓

SVACS Contract Validation Passed

↓

Artifact Stored in Bucket

↓

Response Returned
```

---

## Runtime Result

No runtime failures were observed during the validation scenarios.
