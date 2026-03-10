"""
Comprehensive determinism validation and conflict detection tests.
Tests verify:
- Deterministic, rule-based truth classification (levels 0-4)
- Conflict detection via structural contradiction detection
- Idempotence: same inputs always produce same outputs
- No randomness, no schema mutation
"""
import copy
import json
from truth_classifier import classify_claim
from conflict_detector import detect_conflicts


# =============================================================================
# TRUTH CLASSIFIER TESTS - Rule-Based Levels 0-4
# =============================================================================

def test_classify_level_4_direct_evidence():
    """Level 4: Direct documented/primary evidence"""
    e = {"sources": [], "evidence": [{"evidence_type": "direct"}]}
    assert classify_claim(e) == 4


def test_classify_level_4_direct_precedence():
    """Level 4 takes precedence even with other evidence types"""
    e = {
        "sources": ["s1"],
        "evidence": [
            {"evidence_type": "report"},
            {"evidence_type": "direct"},
            {"evidence_type": "institutional"},
        ]
    }
    assert classify_claim(e) == 4


def test_classify_level_3_institutional():
    """Level 3: Institutional/primary authority source"""
    e = {"sources": [], "evidence": [{"evidence_type": "institutional"}]}
    assert classify_claim(e) == 3


def test_classify_level_3_institutional_precedence():
    """Level 3 takes precedence over multi-source (level 2)"""
    e = {
        "sources": ["s1", "s2"],
        "evidence": [{"evidence_type": "institutional"}]
    }
    assert classify_claim(e) == 3


def test_classify_level_2_multi_source():
    """Level 2: Multi-source corroboration (>=2 distinct sources)"""
    e = {"sources": ["source_a", "source_b"], "evidence": []}
    assert classify_claim(e) == 2


def test_classify_level_2_multi_source_three():
    """Level 2: Three distinct sources"""
    e = {"sources": ["a", "b", "c"], "evidence": []}
    assert classify_claim(e) == 2


def test_classify_level_2_two_reports():
    """Level 2: Two or more report-type evidence items"""
    e = {
        "sources": [],
        "evidence": [
            {"evidence_type": "report"},
            {"evidence_type": "report"}
        ]
    }
    assert classify_claim(e) == 2


def test_classify_level_2_multi_source_and_reports():
    """Level 2 when both multi-source and multiple reports"""
    e = {
        "sources": ["s1", "s2"],
        "evidence": [
            {"evidence_type": "report"},
            {"evidence_type": "report"}
        ]
    }
    assert classify_claim(e) == 2


def test_classify_level_1_single_source():
    """Level 1: Single-source report"""
    e = {"sources": ["only_one"], "evidence": []}
    assert classify_claim(e) == 1


def test_classify_level_1_single_report():
    """Level 1: Single report-type evidence item"""
    e = {"sources": [], "evidence": [{"evidence_type": "report"}]}
    assert classify_claim(e) == 1


def test_classify_level_1_single_source_with_report():
    """Level 1: Single source with report evidence"""
    e = {
        "sources": ["s1"],
        "evidence": [{"evidence_type": "report"}]
    }
    assert classify_claim(e) == 1


def test_classify_level_0_unverified():
    """Level 0: Unverified claim (no sources, no evidence)"""
    e = {"sources": [], "evidence": []}
    assert classify_claim(e) == 0


def test_classify_level_0_empty_fields():
    """Level 0: When sources and evidence are completely absent"""
    e = {}
    assert classify_claim(e) == 0


def test_classify_level_0_null_values():
    """Level 0: When sources/evidence are None"""
    e = {"sources": None, "evidence": None}
    assert classify_claim(e) == 0


def test_classify_level_0_empty_nested():
    """Level 0: When evidence list contains invalid items"""
    e = {"sources": [], "evidence": [{"not_evidence_type": "foo"}]}
    assert classify_claim(e) == 0


# =============================================================================
# DETERMINISM TESTS - Idempotence & Replay Validation
# =============================================================================

def test_determinism_simple_case():
    """Same input produced same classification across multiple runs"""
    base = {"sources": ["s1"], "evidence": [{"evidence_type": "report"}]}
    results = [classify_claim(copy.deepcopy(base)) for _ in range(10)]
    assert len(set(results)) == 1, "Non-deterministic: multiple results"
    assert results[0] == 1


def test_determinism_complex_case():
    """Complex multi-field case is deterministic"""
    base = {
        "sources": ["cnn", "bbc", "reuters"],
        "evidence": [
            {"evidence_type": "report"},
            {"evidence_type": "institutional"},
            {"metadata": "extra"}
        ]
    }
    results = [classify_claim(copy.deepcopy(base)) for _ in range(10)]
    assert len(set(results)) == 1
    assert results[0] == 3


def test_determinism_with_deepcopy():
    """Deepcopy preserves determinism (no reference issues)"""
    base = {"sources": ["a"], "evidence": [{"evidence_type": "direct"}]}
    original = classify_claim(base)
    for _ in range(100):
        deepcopied = classify_claim(copy.deepcopy(base))
        assert deepcopied == original == 4


def test_determinism_across_json_roundtrip():
    """JSON serialization/deserialization preserves determinism"""
    base = {
        "sources": ["s1", "s2"],
        "evidence": [{"evidence_type": "report"}]
    }
    result_before = classify_claim(base)
    
    # Roundtrip through JSON
    json_str = json.dumps(base)
    restored = json.loads(json_str)
    result_after = classify_claim(restored)
    
    assert result_before == result_after == 2


def test_determinism_no_field_order_dependency():
    """Field order in dict does not affect result"""
    e1 = {"sources": ["a", "b"], "evidence": []}
    e2 = {"evidence": [], "sources": ["a", "b"]}
    # Both dicts have same content, different declaration order
    assert classify_claim(e1) == classify_claim(e2) == 2


# =============================================================================
# CONFLICT DETECTION TESTS - Structural Contradiction Detection
# =============================================================================

def test_conflict_numeric_values():
    """Numeric conflict: different values for same key"""
    evs = [
        {"registry_reference_id": "r1", "value": 10},
        {"registry_reference_id": "r1", "value": 11},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is True


def test_conflict_same_numeric_no_conflict():
    """Same numeric values are not a conflict"""
    evs = [
        {"registry_reference_id": "r1", "value": 10},
        {"registry_reference_id": "r1", "value": 10},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is False


def test_conflict_categorical_status():
    """Categorical conflict: different status values"""
    evs = [
        {"registry_reference_id": "r1", "status": "open"},
        {"registry_reference_id": "r1", "status": "closed"},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is True


def test_conflict_state_field():
    """Conflict detection for 'state' field"""
    evs = [
        {"registry_reference_id": "r1", "state": "active"},
        {"registry_reference_id": "r1", "state": "inactive"},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is True


def test_conflict_event_state_field():
    """Conflict detection for 'event_state' field"""
    evs = [
        {"registry_reference_id": "r1", "event_state": "pending"},
        {"registry_reference_id": "r1", "event_state": "completed"},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is True


def test_conflict_multiple_fields():
    """Conflict in any field is detected"""
    evs = [
        {"registry_reference_id": "r1", "value": 100, "location": "NYC"},
        {"registry_reference_id": "r1", "value": 100, "location": "LA"},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is True


def test_conflict_boolean_mismatch():
    """Boolean field mismatch is a conflict"""
    evs = [
        {"registry_reference_id": "r1", "verified": True},
        {"registry_reference_id": "r1", "verified": False},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is True


def test_no_conflict_metadata_ignored():
    """Metadata timestamps are excluded from conflict detection"""
    evs = [
        {"registry_reference_id": "r1", "value": 10, "updated_at": "2024-01-01"},
        {"registry_reference_id": "r1", "value": 10, "updated_at": "2024-01-02"},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is False


def test_no_conflict_partial_fields():
    """Conflict only on fields present in both events"""
    evs = [
        {"registry_reference_id": "r1", "value": 10, "extra_a": "x"},
        {"registry_reference_id": "r1", "value": 10, "extra_b": "y"},
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is False


def test_conflict_grouping_by_registry_id():
    """Events grouped correctly by registry_reference_id"""
    evs = [
        {"registry_reference_id": "r1", "value": 10},
        {"registry_reference_id": "r1", "value": 20},  # conflict with above
        {"registry_reference_id": "r2", "value": 30},
        {"registry_reference_id": "r2", "value": 30},  # no conflict
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is True
    assert res["r2"] is False


def test_conflict_missing_registry_id():
    """Events without registry_reference_id are treated independently"""
    evs = [
        {"value": 10},  # synthetic id __local__0
        {"value": 20},  # synthetic id __local__1
    ]
    res = detect_conflicts(evs)
    # Each gets synthetic id, so no conflict since they're different ids
    assert res.get("__local__0") is False
    assert res.get("__local__1") is False


def test_conflict_deterministic():
    """Conflict detection is deterministic across runs"""
    evs = [
        {"registry_reference_id": "r1", "value": 10, "status": "active"},
        {"registry_reference_id": "r1", "value": 15, "status": "active"},
    ]
    results = [detect_conflicts(copy.deepcopy(evs)) for _ in range(10)]
    # All should have r1 -> True
    assert all(r["r1"] is True for r in results)


def test_conflict_three_way_contradiction():
    """Multiple pairwise conflicts detected across three events"""
    evs = [
        {"registry_reference_id": "r1", "value": 10},
        {"registry_reference_id": "r1", "value": 20},  # conflict with 1st
        {"registry_reference_id": "r1", "value": 30},  # conflicts with both
    ]
    res = detect_conflicts(evs)
    assert res["r1"] is True


# =============================================================================
# INTEGRATION TESTS - Combined Truth + Conflict
# =============================================================================

def test_integration_classify_and_detect():
    """End-to-end: classify truth level and detect conflicts"""
    events = [
        {
            "registry_reference_id": "event1",
            "sources": ["bbc", "cnn"],
            "evidence": [{"evidence_type": "institutional"}],
            "value": 50,
            "status": "reported"
        },
        {
            "registry_reference_id": "event1",
            "sources": ["bbc", "cnn"],
            "evidence": [{"evidence_type": "institutional"}],
            "value": 50,
            "status": "reported"
        }
    ]
    
    # All classify as level 3 (institutional)
    assert all(classify_claim(e) == 3 for e in events)
    
    # No conflict since values/status are the same
    conflicts = detect_conflicts(events)
    assert conflicts["event1"] is False


def test_integration_conflicted_truth_levels():
    """Conflicted events have different truth levels"""
    events = [
        {
            "registry_reference_id": "event2",
            "sources": ["s1"],
            "evidence": [{"evidence_type": "direct"}],
            "amount": 1000
        },
        {
            "registry_reference_id": "event2",
            "sources": ["s2"],
            "evidence": [{"evidence_type": "report"}],
            "amount": 2000  # numeric conflict
        }
    ]
    
    # Different truth levels
    levels = [classify_claim(e) for e in events]
    assert levels == [4, 1]
    
    # Conflict flag set
    conflicts = detect_conflicts(events)
    assert conflicts["event2"] is True
