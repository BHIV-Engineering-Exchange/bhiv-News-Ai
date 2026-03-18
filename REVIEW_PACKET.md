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
  "event_id": "917282859967224a5dbc162f0186a3e17df81cd3975c0795f4e9707fefbece96",
  "truth_level": 3,
  "conflict_flag": false,
  "registry_reference_id": "REG_999"
}
```

---

## 4. WHAT WAS BUILT IN THIS TASK

- **What was added:** `truth_classifier.py`, `conflict_detector.py`, `classification_rules.md`, `conflict_detection_rules.md`, `determinism_validation_report.md`, `validate_truth_layer.py`, `.env.example`.
- **What was modified:** `main.py` (middleware logging hooks), `monitor_backend.py` (daemon mode), `demo_check.py` (latency checks), `DEMO_RECOVERY.md` (operator guide).
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
--- Starting Determinism Validation ---
Event 1: { "event_id": "91728285...", "truth_level": 3, "conflict_flag": false }
Event 2: { "event_id": "91728285...", "truth_level": 3, "conflict_flag": false }
✅ PASSED: Identical inputs produced identical outputs.
--- Testing Conflict Detection ---
Conflict Flag for incompatible numeric values: True
✅ PASSED: Conflict detected correctly.
```
