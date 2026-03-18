# REVIEW_PACKET.md

## 1. ENTRY POINT

**Frontend entry:**
Path: `N/A`
Backend-focused task; no frontend entry points modified.

**Backend entry:**
Path: `c:\Users\user11\Desktop\NEWS AI\News-Ai-main\News-ai-master\unified_tools_backend\main.py`
FastAPI server hosting truth ingestion hooks and monitoring middleware.

---

## 2. CORE EXECUTION FLOW (MAX 3 FILES ONLY)

**File 1:**
Path: `c:\Users\user11\Desktop\NEWS AI\News-Ai-main\sankalp-insight-node\classification\truth_classifier.py`
What it does: Deterministic rule-based classification of truth signals (Levels 0–4).

**File 2:**
Path: `c:\Users\user11\Desktop\NEWS AI\News-Ai-main\sankalp-insight-node\classification\conflict_detector.py`
What it does: Detects structural contradictions for identical registry_reference_id without resolution.

**File 3:**
Path: `c:\Users\user11\Desktop\NEWS AI\News-Ai-main\monitor_backend.py`
What it does: Persistent 30s monitoring loop that validates endpoint health and automatically logs failures to `newsai_error_log.json`.

---

## 3. LIVE FLOW (ACTUAL EXECUTION)

**User action:**
Replay ingestion of a verified news source.

**System flow:**
API Hook -> `classify_truth_level` (assigned 3) -> `detect_conflicts` (assigned false) -> `newsai_error_log.json` -> `monitor_report.json`

**Real JSON response:**
```json
{
  "event_id": "b1e9865b4455b69f3f13985e2ad239d9292fb64c13faed037ce088f509142f29",
  "truth_level": 3,
  "conflict_flag": false,
  "registry_reference_id": "REGISTRY_ID_001"
}
```

---

## 4. WHAT WAS BUILT IN THIS TASK

- **What was added:** `sankalp-insight-node/classification/truth_classifier.py`, `sankalp-insight-node/classification/conflict_detector.py`, `truth_classification_rules.md`, `conflict_detection_rules.md`, `determinism_validation_report.md`, `validate_truth_engine.py`, `example_output_events.md`.
- **What was modified:** Updated `REVIEW_PACKET.md` with finalized execution paths.
- **What was NOT touched:** Source hashing logic, database schema, frontend UI components.

---

## 5. FAILURE CASES

**What breaks:**
- **Backend down:** Monitor logs `TIMEOUT/ERROR` to `newsai_error_log.json`; Safety Checker returns `UNSAFE`.
- **Invalid input:** Truth classifier defaults to `Level 0` (Unverified).
- **Contradictory values:** Conflict detector flags `conflict_flag: true` but preserves data without resolution.

---

## 6. PROOF

**Console output:**
```text
Event 1: {
  "event_id": "b1e9865b4455b69f3f13985e2ad239d9292fb64c13faed037ce088f509142f29",
  "source_hash": "SOURCE_HASH_001",
  "truth_level": 3,
  "conflict_flag": false,
  "registry_reference_id": "REGISTRY_ID_001"
}
Event 2: {
  "event_id": "b1e9865b4455b69f3f13985e2ad239d9292fb64c13faed037ce088f509142f29",
  "source_hash": "SOURCE_HASH_001",
  "truth_level": 3,
  "conflict_flag": false,
  "registry_reference_id": "REGISTRY_ID_001"
}

--- Testing Conflict Detection & Normalization ---
Conflict Flag for 5000 vs '5000.0': False
Conflict Flag for False vs 'False': False
Conflict Flag for 'verified' vs 'closed': True
✅ All Conflict Logic Passed.
```
