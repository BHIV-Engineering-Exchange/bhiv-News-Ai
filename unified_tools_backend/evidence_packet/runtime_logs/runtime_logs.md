# Replay Validation Runtime Logs

## First Execution (Replay MISS)

### Request

**Endpoint**

```http
POST /api/v1/intelligence/image
```

**Input**

```
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

# Second Execution (Replay HIT)

### Request

**Endpoint**

```http
POST /api/v1/intelligence/image
```

**Input**

```
cargo_ship.jpg
```

*(Same image uploaded again.)*

### Runtime Output

```text
[Replay] Fingerprint:
sha256:cf1bcaf2dd58678be77f50073e0656ea56546799248d1dfd04c625b86ed1184a

Replay Status:
HIT

Vision Runtime:
Skipped (cached replay used)
```

### Replay Information

```json
{
  "status": "HIT",
  "input_fingerprint": "sha256:cf1bcaf2dd58678be77f50073e0656ea56546799248d1dfd04c625b86ed1184a",
  "original_trace_id": "SAM-09f3a454-e930-4b4c-a1e8-68db52c316bd"
}
```

---

# Validation Summary

| Validation | Result |
|------------|--------|
| SHA-256 Fingerprint Generation | ✅ PASS |
| Replay MISS | ✅ PASS |
| Replay HIT | ✅ PASS |
| Live Vision Runtime Invocation | ✅ PASS |
| Vision Runtime Replay ID Preservation | ✅ PASS |
| Execution ID Propagation | ✅ PASS |
| Trace ID Propagation | ✅ PASS |
| OCR Normalization | ✅ PASS |
| Canonical Intelligence Generation | ✅ PASS |
| Processing Trace Generation | ✅ PASS |
| Runtime Metrics Collection | ✅ PASS |
| SVACS Contract Validation | ✅ PASS |
| HTTP Response | ✅ 200 OK |