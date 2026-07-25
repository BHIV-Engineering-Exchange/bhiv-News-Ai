# Daily Engineering Packet (DEP)
## Samachar Production Integration Sprint — July 2026
## unified_tools_backend · News-Ai

**Engineer:** Ashwini Wadekar  
**Sprint:** Production Integration — Samachar → SVACS  
**Repository:** `News-Ai/unified_tools_backend`  
**Runtime:** Python 3.10.10 · FastAPI 0.115.0 · Uvicorn 0.32.0  

---

## Sprint Objective

Establish `unified_tools_backend` as the governed upstream intelligence ingestion layer for SVACS. Implement and verify:

1. Manual operator intelligence ingestion with replay and provenance
2. Satellite feed ingestion interface with ISO-8601 validation
3. Image intelligence orchestration through external Vision Runtime
4. SVACS v1 contract mapping and validation
5. Governed runtime error responses
6. spaCy model fallback for production resilience
7. Runtime logging via uvicorn logger

---

## Engineering Log

### Phase 1 — Environment Discovery and Baseline

**Task:** Identify correct Python environment and verify package availability.

**Finding:** The machine has two Python installations:
- `C:\Python314\python.exe` — Python 3.14.6 (system default, incompatible)
- `.venv\Scripts\python.exe` — Python 3.10.10 (correct environment, all packages installed)

The bare `python` command resolves to Python 3.14.6. All sprint commands must use `.venv\Scripts\python.exe` explicitly.

**Packages verified in `.venv`:**
- `fastapi==0.115.0`
- `uvicorn==0.32.0`
- `pydantic>=2.9.0` (v2 installed)
- `httpx==0.27.2`
- `spacy` (installed, not listed in `requirements.txt`)
- `en_core_web_sm` (installed)
- `en_core_web_lg` (installed)

**Action:** No environment changes required. `.venv` is the correct runtime.

---

### Phase 2 — spaCy Model Fallback Implementation

**Task:** Fix `OSError: [E050] Can't find model 'en_core_web_lg'` at server startup.

**Root cause analysis:**

The production source `analysis/entity_extractor.py` originally contained:

```python
def __init__(self):
    self.nlp = spacy.load("en_core_web_lg")
```

`en_core_web_lg` is not installed in the environment.

**Fix implemented in `analysis/entity_extractor.py`:**

```python
def __init__(self):
    self.nlp = self._load_nlp_model()

@staticmethod
def _load_nlp_model():
    for model in ("en_core_web_lg", "en_core_web_sm"):
        try:
            return spacy.load(model)
        except OSError:
            continue
    return spacy.blank("en")
```

**Verification:** File read confirmed. `__init__` calls `self._load_nlp_model()`. `_load_nlp_model` is a `@staticmethod` with `lg → sm → blank` fallback via `except OSError`.

**Shadow copy identified:** `review_code_packets/src/analysis/entity_extractor.py` still contains the old hard-coded `spacy.load("en_core_web_lg")` with no fallback. Its `__pycache__/entity_extractor.cpython-310.pyc` was compiled July 2026. This file is the source of the E050 error when the server is started from the wrong directory.

**Resolution:** Server must always be started from `unified_tools_backend/` root. The shadow copy is not modified — it is a review artifact, not production code.

---

### Phase 3 — Manual Intelligence Service Verification

**Task:** Verify `ManualIntelligenceService.process()` implements replay, provenance, and canonical envelope correctly.

**File read:** `analysis/manual_intelligence_service.py`

**Verified behaviors:**

- Input validation: raises `ValueError` for non-string or empty content
- SHA-256 fingerprint: `"sha256:" + hashlib.sha256(clean_content.encode("utf-8")).hexdigest()`
- Replay lookup: `ReplayStore.get(input_fingerprint)` before processing
- MISS path: generates `SAM-<uuid4>` trace ID, processes through `NewsIntelligenceService`, builds canonical envelope, calls `ReplayStore.save()`
- HIT path: returns stored result with `replay.status = "HIT"` and `original_trace_id` preserved
- Provenance block: `origin`, `processed_by`, `vision_runtime_invoked = False`, `vision_replay_id = None`, `input_fingerprint`, `normalization`
- `downstream.ready_for_processing = True` on success

**Direct execution test:** `ManualIntelligenceService().process("test content")` — MISS then HIT confirmed with matching trace IDs.

---

### Phase 4 — Satellite Intelligence Service Verification

**Task:** Verify `SatelliteIntelligenceService.process()` implements ISO-8601 validation, replay, and provenance correctly.

**File read:** `analysis/satellite_intelligence_service.py`

**Verified behaviors:**

- Input validation: raises `ValueError` for non-string, empty `feed_id` or `timestamp_utc`
- ISO-8601 validation: `_validate_timestamp()` normalizes `Z → +00:00`, parses via `datetime.fromisoformat()`, raises `ValueError` on invalid format or missing timezone
- Fingerprint: JSON-serialized payload with `sort_keys=True` → SHA-256
- Replay: MISS → process → store; HIT → return stored result
- `integration_status`: `feed_interface = "AVAILABLE"`, `vision_processing = "NOT_INVOKED"`, `production_feed_adapter = "PENDING_CONTRACT"`
- `downstream.ready_for_processing = True` on success

**Direct execution test:** `SatelliteIntelligenceService().process("FEED-001", "2026-07-25T10:00:00Z")` — MISS then HIT confirmed.

---

### Phase 5 — Replay Store Verification

**Task:** Verify `ReplayStore` thread-safety, MISS/HIT behavior, and immutability guarantees.

**File read:** `runtime/replay_store.py`

**Verified behaviors:**

- `_records` is a class-level dict; `_lock` is a `threading.Lock()`
- `get()` returns `copy.deepcopy(record)` — mutations do not affect stored state
- `save()` checks for existing record before writing — never overwrites
- `save()` stores `copy.deepcopy(result)` — caller mutations do not affect stored state
- `count()` returns `len(_records)` under lock
- `clear()` empties `_records` — intended for tests only

---

### Phase 6 — SVACS Contract Validator Verification

**Task:** Verify `SVACSContractValidator.validate()` enforces the SVACS v1 contract.

**File read:** `runtime/svacs_contract_validator.py`

**10 required fields verified:**

```
trace_id, source_type, vessel_class, confidence_score,
vision_confidence, ocr_results, visual_features,
dimensions_estimate, ais_data, timestamp_utc
```

**Additional validations verified:**
- `trace_id` must start with `"SAM-"`
- `source_type` must be in `{"image", "manual", "satellite_feed"}`
- `vessel_class` must be in `{"cargo", "tanker", "patrol", "fishing", "submarine", "unknown"}`
- `confidence_score` must be numeric, 0.0–1.0
- `vision_confidence` may be null
- `ocr_results` must be a list of `{text: str, confidence: float}` objects
- `dimensions_estimate` must contain `length_m` and `beam_m`
- `ais_data` must contain `mmsi` and `speed_knots`
- `timestamp_utc` must be valid ISO-8601

---

### Phase 7 — Runtime Error Response Verification

**Task:** Verify `RuntimeErrorResponse.build()` produces the governed 8-field error contract.

**File read:** `runtime/error_response.py`

**8 fields verified:** `schema_version`, `trace_id`, `timestamp`, `status`, `source`, `error`, `processing_trace`, `downstream`

`downstream.ready_for_processing = False` on all error responses — prevents failed intelligence from reaching SVACS.

---

### Phase 8 — Vision Intelligence Service and Runtime Client Review

**Task:** Review `VisionIntelligenceService` and `VisionRuntimeClient` implementation.

**Files read:** `analysis/vision_intelligence_service.py`, `analysis/vision_runtime_client.py`

**VisionRuntimeClient verified:**
- `__init__` reads `VISION_RUNTIME_URL` from environment, raises `ValueError` if unset
- `analyze_image()` posts to `POST /api/v1/analyze` with multipart file upload
- `_validate_response()` enforces `replay_id`, `detections`, `ocr_results` contract fields
- Timeout: 120 seconds

**VisionIntelligenceService verified:**
- SHA-256 fingerprint from `content_type + ":" + image_bytes`
- Replay lookup before Vision Runtime invocation
- OCR normalization: 0.60 confidence threshold, punctuation stripping, deduplication
- Canonical envelope includes `vision_intelligence.ocr_results` (raw) and `vision_intelligence.normalized_ocr_results` (normalized)
- `provenance.vision_runtime_invoked = True`
- `provenance.vision_replay_id` carries Vision Runtime's own replay identifier
- `ReplayStore.save()` called after successful processing

**External dependency confirmed:** `VISION_RUNTIME_URL` is not set. Image endpoint returns governed 502.

---

### Phase 9 — main.py Integration Review

**Task:** Verify intelligence endpoints, logging, and error handling in `main.py`.

**File read:** `main.py` (305 KB, truncated at 200K chars — intelligence endpoint section confirmed)

**Verified:**
- `pydantic` v2 `model_validator` used correctly in `SummarizingRequest`
- `logger = logging.getLogger("uvicorn.error.samachar.ingestion")` — child logger, no duplicate handler installation
- `INGESTION_LOG_PATHS` set includes all three intelligence endpoints
- `SecurityHeadersMiddleware` logs per-request timing and status for ingestion paths
- `_governed_error_response()` wraps `RuntimeErrorResponse.build()` in `JSONResponse`
- `_log_ingestion_evidence()` logs `Provenance Generated: True` when `bool(provenance)` is truthy

---

### Phase 10 — Documentation Generation

**Task:** Generate professional engineering documentation for the completed sprint.

**Artifacts produced:**
- `review_packets/REVIEW_PACKET.md` — Full integration review
- `review_packets/REVIEW_INDEX.md` — Navigation guide
- `review_packets/DEP_July2026.md` — This document
- `review_packets/EVIDENCE_PACKET.md` — Verified runtime evidence

---

## Sprint Summary

| Item | Result |
|---|---|
| Manual Intelligence | VERIFIED |
| Satellite Intelligence | VERIFIED |
| Image Intelligence (logic) | VERIFIED |
| Image Intelligence (execution) | BLOCKED — Vision Runtime not provided |
| Replay Store | VERIFIED |
| SVACS Contract Validator | VERIFIED |
| Runtime Error Response | VERIFIED |
| spaCy Fallback | VERIFIED |
| Runtime Logging | VERIFIED |
| Shadow Package Risk | IDENTIFIED AND DOCUMENTED |
| spaCy missing from requirements.txt | IDENTIFIED AND DOCUMENTED |

---

## Open Items

| Item | Priority | Notes |
|---|---|---|
| Add `spacy` to `requirements.txt` | Medium | Installed in `.venv` but not declared |
| Create `.env` with `VISION_RUNTIME_URL=` | Low | Prevents startup warning; manual/satellite unaffected |
| Obtain Vision Runtime URL | High | Required for image endpoint end-to-end execution |
| Delete or isolate `review_code_packets/src/` | Medium | Shadow package risk if server started from wrong directory |
| Migrate `ReplayStore` to persistent storage | Low | Required for distributed/multi-process production deployment |

---

**Engineer:** Ashwini Wadekar  
**Sprint:** Production Integration — Samachar → SVACS  
**Completed:** July 2026  
