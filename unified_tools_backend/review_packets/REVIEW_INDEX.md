# REVIEW INDEX — Samachar Production Integration
## unified_tools_backend · July 2026

This index maps every review artifact to its location and purpose.

---

## Primary Documents

| Document | Path | Purpose |
|---|---|---|
| REVIEW_PACKET.md | `review_packets/REVIEW_PACKET.md` | Full integration review — all sections |
| REVIEW_INDEX.md | `review_packets/REVIEW_INDEX.md` | This file — navigation guide |
| Daily Engineering Packet | `review_packets/DEP_July2026.md` | Day-by-day engineering log |
| Evidence Packet | `review_packets/EVIDENCE_PACKET.md` | Verified runtime evidence |

---

## Source Files — Production (Active)

| File | Path | Sprint Role |
|---|---|---|
| `entity_extractor.py` | `analysis/entity_extractor.py` | NER with spaCy fallback |
| `manual_intelligence_service.py` | `analysis/manual_intelligence_service.py` | Manual ingestion, replay, provenance |
| `satellite_intelligence_service.py` | `analysis/satellite_intelligence_service.py` | Satellite feed ingestion, ISO-8601 validation |
| `vision_intelligence_service.py` | `analysis/vision_intelligence_service.py` | Image orchestration, OCR normalization |
| `vision_runtime_client.py` | `analysis/vision_runtime_client.py` | External Vision Runtime HTTP client |
| `svacs_intelligence_mapper.py` | `analysis/svacs_intelligence_mapper.py` | Canonical → SVACS v1 translation |
| `replay_store.py` | `runtime/replay_store.py` | Thread-safe in-memory replay store |
| `svacs_contract_validator.py` | `runtime/svacs_contract_validator.py` | SVACS v1 contract validation |
| `error_response.py` | `runtime/error_response.py` | Governed runtime error builder |
| `main.py` | `main.py` | FastAPI application, intelligence endpoints |

---

## Source Files — Shadow Copy (Do Not Import)

| File | Path | Issue |
|---|---|---|
| `entity_extractor.py` (shadow) | `review_code_packets/src/analysis/entity_extractor.py` | Hard-coded `spacy.load("en_core_web_lg")`, no fallback, compiled `.pyc` present |

> The shadow copy must never appear on `sys.path`. Always start the server from `unified_tools_backend/` using `.venv\Scripts\python.exe`.

---

## Test Files

| File | Path | Validates |
|---|---|---|
| `test_samachar_svacs_integration.py` | `tests/` | End-to-end manual, satellite, SVACS mapping |
| `test_replay_store.py` | `tests/` | ReplayStore MISS/HIT |
| `test_svacs_contract_validator.py` | `tests/` | SVACS v1 contract validation |
| `test_error_response.py` | `tests/` | Governed error response structure |
| `test_manual_intelligence_service.py` | `tests/` | Manual service unit tests |
| `test_satellite_intelligence_service.py` | `tests/` | Satellite service unit tests |
| `test_vision_intelligence_service.py` | `tests/` | Vision service unit tests |

---

## Screenshots

Located in `review_packets/screenshots/`:

| File | Shows |
|---|---|
| `01_manual_ingestion.png` | Manual endpoint response |
| `02_satellite_feed_interface.png` | Satellite endpoint response |
| `03_image_svacs_payload.png` | Image endpoint governed error |
| `04_replay_miss.png` | Replay MISS |
| `05_replay_hit.png` | Replay HIT |
| `06_svacs_contract_validation.png` | SVACS contract validator |
| `07_governed_error_response.png` | Governed error response |
| `08_samachar_svacs_integration.png` | Integration test suite |
| `Samachar-SVACS testing & validation results.png` | Full validation summary |

---

## Architecture Documents

| File | Path | Content |
|---|---|---|
| `integration_architecture.md` | `review_packets/architecture/` | System boundary diagram |
| `pipeline_flow.md` | `review_packets/architecture/` | Processing pipeline flow |

---

## Contracts

| File | Path | Content |
|---|---|---|
| `svacs_intelligence_contract_v1.json` | `contracts/` | Frozen SVACS v1 contract definition |

---

## Quick Verification Commands

```bash
# Run primary integration suite
.venv\Scripts\python.exe -m pytest tests/test_samachar_svacs_integration.py -s

# Run replay store tests
.venv\Scripts\python.exe -m pytest tests/test_replay_store.py -s

# Run SVACS contract validator tests
.venv\Scripts\python.exe -m pytest tests/test_svacs_contract_validator.py -s

# Run governed error response tests
.venv\Scripts\python.exe -m pytest tests/test_error_response.py -s

# Run full regression suite
.venv\Scripts\python.exe -m pytest -q

# Start server (correct environment and working directory)
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Key Facts for Reviewer

- All sprint logic is verified in the production source files
- The only incomplete execution path is the image endpoint, blocked by the missing external Vision Runtime service
- `VISION_RUNTIME_URL` is not set — no `.env` file exists
- The correct Python environment is `.venv` (Python 3.10.10)
- The system `python` command resolves to Python 3.14.6 — do not use it
- `spacy` is missing from `requirements.txt` but is installed in `.venv`

---

**Contract Version:** `1.0.0`  
**Downstream Consumer:** SVACS  
