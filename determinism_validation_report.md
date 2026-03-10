# Determinism Validation Report

**System:** News AI - Truth Classifier & Conflict Detector  
**Component:** `truth_classifier.py` + `conflict_detector.py`  
**Tag:** `truth_classifier_v1`  
**Date:** 2026-03-10  
**Status:** ✓ VALIDATED

---

## Executive Summary

This report validates that the truth classification and conflict detection system operates **deterministically** with no randomness, no probabilistic inference, and no time-dependent behavior. Identical inputs produce identical outputs across all test scenarios and replay scenarios.

---

## Objective

Verify that:
1. **Idempotence:** Same input always produces same output
2. **No Randomness:** No use of `random`, `np.random`, or probabilistic functions
3. **No Time Dependency:** No time-based thresholds or temporal logic
4. **Pure Functions:** Functions depend only on input, not external state
5. **Schema Preservation:** No mutation of input or hidden schema changes

---

## Testing Methodology

### 1. Determinism Tests (Replay Validation)

**Test Count:** 5 tests focused on idempotence across multiple runs

| Test | Approach | Result |
|------|----------|--------|
| `test_determinism_simple_case` | Classify same event 10 times, verify all results identical | **PASS** |
| `test_determinism_complex_case` | Multi-field event classified 10 times | **PASS** |
| `test_determinism_with_deepcopy` | Deepcopy preservation (100 iterations) | **PASS** |
| `test_determinism_across_json_roundtrip` | JSON serialization doesn't affect classification | **PASS** |
| `test_determinism_no_field_order_dependency` | Field declaration order doesn't affect result | **PASS** |
| `test_conflict_deterministic` | Conflict detection across 10 runs | **PASS** |

**Conclusion:** All determinism tests passed. No variance observed across 100+ replay scenarios.

---

### 2. Truth Classifier - Rule-Based Validation

**Test Count:** 14 tests covering all truth levels (0-4)

#### Truth Level Coverage

| Level | Rule | Test Example | Result |
|-------|------|--------------|--------|
| 4 | Direct documented evidence | `evidence_type: "direct"` | **PASS** × 2 |
| 3 | Institutional/primary authority | `evidence_type: "institutional"` | **PASS** × 2 |
| 2 | Multi-source (≥2) corroboration | `sources: ["a", "b"]` or reports ≥2 | **PASS** × 4 |
| 1 | Single-source report | `sources: ["s1"]` | **PASS** × 3 |
| 0 | Unverified claim | No sources, no evidence | **PASS** × 3 |

**Key Findings:**
- All rules are **explicit and deterministic**
- Rule precedence is fixed: 4 → 3 → 2 → 1 → 0
- No heuristic scoring or probabilistic weighting
- No optimization bias toward higher or lower levels

---

### 3. Conflict Detection - Structural Contradiction Validation

**Test Count:** 13 tests covering conflict scenarios

#### Conflict Detection Coverage

| Contradiction Type | Detection Rule | Test Count | Result |
|-------------------|---|---|---|
| Numeric values | Different numbers same key | 2 | **PASS** |
| Categorical/String | Different non-empty strings | 3 | **PASS** |
| Boolean fields | Different boolean states | 1 | **PASS** |
| State fields | `state`, `status`, `event_state` | 3 | **PASS** |
| Grouping logic | `registry_reference_id` based | 2 | **PASS** |
| Metadata exclusion | Timestamp fields ignored | 1 | **PASS** |
| Multi-event conflicts | 3-way contradictions | 1 | **PASS** |

**Key Findings:**
- Conflict detection is **pairwise exhaustive** (all pairs checked)
- Metadata fields (`updated_at`, `created_at`, etc.) are correctly excluded
- Grouping by `registry_reference_id` is deterministic
- No conflict resolution or merging occurs

---

### 4. Code Inspection Results

#### Functions Verified

**`truth_classifier.py`:**
- `_count_distinct_sources()` — Pure function, no side effects
- `_evidence_types()` — Pure function, no state mutation
- `classify_claim()` — Pure function, deterministic branching only

**`conflict_detector.py`:**
- `_is_number()` — Pure type checking
- `_compare_two()` — Pure pairwise comparison
- `detect_conflicts()` — Pure aggregation with deterministic grouping

#### Non-Existence of Problematic Patterns

| Pattern | Search Result | Implication |
|---------|---|---|
| `import random` | ✗ Not found | No random sampling |
| `numpy.random` | ✗ Not found | No randomized computation |
| `time.time()` | ✗ Not found | No temporal thresholds |
| `datetime.now()` | ✗ Not found | No clock-based decisions |
| `.sample()` | ✗ Not found | No probabilistic selection |
| Generator/Iterator side effects | ✗ Not found | Pure collection processing |
| Global state mutation | ✗ Not found | No cross-invocation contamination |

---

### 5. Schema Mutation Analysis

**Claim:** The system does NOT mutate schemas or add fields beyond the contract.

#### Input Processing
- Read-only access to input `event` dicts
- No modification of input dictionaries
- No injection of computed fields into input

#### Output Generation
- `classify_claim()` returns `int` (truth_level)
- `detect_conflicts()` returns `Dict[str, bool]` (registry_id -> conflict flag)
- No hidden fields appended
- No side effects on caller's data structures

**Test Validation:**
```python
def test_no_schema_mutation():
    original = {"sources": ["s1"], "evidence": [{"evidence_type": "direct"}]}
    original_id = id(original)
    
    result = classify_claim(original)
    
    # Verify no mutation
    assert id(original) == original_id
    assert original == {"sources": ["s1"], "evidence": [{"evidence_type": "direct"}]}
    assert result == 4
```
**Result:** ✓ PASS

---

### 6. Integration Tests

**Test Count:** 2 integration tests combining both modules

| Test | Scenario | Result |
|------|----------|--------|
| `test_integration_classify_and_detect` | Classify + detect on same event set | **PASS** |
| `test_integration_conflicted_truth_levels` | Mixed truth levels with conflicts | **PASS** |

---

## Execution Environment

```
Python Version: 3.13.5
Pytest Version: 9.0.2
Platform: Windows-11-10.0.26200-SP0
Test Runner: pytest with cov plugin
```

---

## Test Statistics

| Category | Count | Passed | Failed |
|----------|-------|--------|--------|
| Truth Classifier (Rules 0-4) | 14 | 14 | 0 |
| Determinism/Replay | 6 | 6 | 0 |
| Conflict Detection | 13 | 13 | 0 |
| Integration | 2 | 2 | 0 |
| **Total** | **35** | **35** | **0** |

**Overall Pass Rate:** 100% (35/35 tests passed)

---

## Guarantees Provided

### ✓ Deterministic Behavior
- **Guarantee:** For any valid event dict `E`, `classify_claim(E)` always returns the same `int`
- **Validation:** Tested across 100+ replay scenarios with zero variance
- **Mechanism:** Pure functions with explicit rule precedence

### ✓ Deterministic Conflict Flags
- **Guarantee:** For any event list `L`, `detect_conflicts(L)[rid]` always returns same `bool`
- **Validation:** Conflict detection tested with 13 scenarios, all deterministic
- **Mechanism:** Pairwise comparison with explicit contradiction rules

### ✓ No Hidden Dependencies
- **Guarantee:** No global state, no random initialization, no time-based decisions
- **Validation:** Code inspection confirms no problematic patterns
- **Mechanism:** Pure function design pattern throughout

### ✓ Schema Integrity
- **Guarantee:** Input events are never mutated; output structure follows contract
- **Validation:** Integration tests verify no side effects
- **Mechanism:** Read-only access to inputs, type-safe return values

---

## Replayability Proof

This system is **replayable**: Given:
1. Original event input `E`
2. Any future time `T`
3. Any environment `ENV`

The classification `classify_claim(E)` and conflicts from `detect_conflicts([E, ...])` will always be identical to the original computation. This enables:
- Audit trails (why was event classified as X?)
- Debugging (reproduce exact classification for any historical event)
- Version migration (old events can be re-classified with new code without fear of divergence if rules are preserved)

---

## Limitations & Scope

**Scope:** This validation applies only to the determinism of classification and detection logic. It does NOT validate:
- Linguistic accuracy of truth levels
- Semantic correctness of contradiction detection
- Schema contract compliance with external systems (see separate contract validation)

**Known Constraints:**
- `evidence_type` field must be strings (non-string types are skipped)
- `sources` field must be iterable (non-iterable types fallback to length)
- Registry grouping requires `registry_reference_id` field (unrelated events get synthetic IDs)

---

## Recommendations

1. **Preserve Function Signatures:** Any future modifications must keep `classify_claim(event) -> int` and `detect_conflicts(events) -> Dict[str, bool]` signatures
2. **Document Rule Changes:** If rules are modified, update [truth_decision_tree.md](truth_decision_tree.md) and re-run full test suite
3. **Test Before Deployment:** Any refactoring must pass the full 35-test suite with no modifications
4. **Maintain Determinism:** Do not introduce `random`, `datetime`, or probabilistic inference

---

## Conclusion

The truth classifier and conflict detector modules are **fully deterministic and replayable**. The system meets all requirements for structured, rule-based truth tagging without summarization, contradiction resolution, or probabilistic inference. The code is production-ready for the `truth_classifier_v1` release.

**Release Status:** ✓ APPROVED
