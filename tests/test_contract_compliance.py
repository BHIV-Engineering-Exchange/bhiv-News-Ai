"""
Contract Compliance Tests for Truth Classifier & Conflict Detector

Validates:
- truth_level field is always int 0-4
- conflict_flag field is always bool
- registry_reference_id handling is correct
- No schema mutations
- Samachar integration contract compliance
"""
import copy
import sys
sys.path.insert(0, '..')
from truth_classifier import classify_claim
from conflict_detector import detect_conflicts
from integrations.samachar_integration import emit_truth_signals, emit_truth_signal_for_event


# =============================================================================
# CONTRACT FIELD VALIDATION TESTS
# =============================================================================

def test_classify_claim_returns_int_truth_level():
    """classify_claim always returns int (truth_level 0-4)"""
    test_cases = [
        {"sources": [], "evidence": []},
        {"sources": ["s1"], "evidence": []},
        {"sources": ["s1", "s2"], "evidence": []},
        {"sources": [], "evidence": [{"evidence_type": "report"}]},
        {"sources": [], "evidence": [{"evidence_type": "institutional"}]},
        {"sources": [], "evidence": [{"evidence_type": "direct"}]},
    ]
    for case in test_cases:
        result = classify_claim(case)
        assert isinstance(result, int), f"Expected int, got {type(result)}"
        assert 0 <= result <= 4, f"Expected truth_level 0-4, got {result}"


def test_conflict_detector_returns_bool_flags():
    """detect_conflicts always returns Dict[str, bool]"""
    test_cases = [
        [],
        [{"registry_reference_id": "r1", "value": 10}],
        [
            {"registry_reference_id": "r1", "value": 10},
            {"registry_reference_id": "r1", "value": 20},
        ],
        [
            {"value": 10},
            {"value": 20},
        ],
    ]
    for case in test_cases:
        result = detect_conflicts(case)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        for rid, flag in result.items():
            assert isinstance(rid, str), f"Expected str key, got {type(rid)}"
            assert isinstance(flag, bool), f"Expected bool value, got {type(flag)}"


# =============================================================================
# SAMACHAR INTEGRATION CONTRACT TESTS
# =============================================================================

def test_emit_truth_signals_required_fields():
    """emitted signals contain required fields per contract"""
    events = [
        {
            "registry_reference_id": "evt1",
            "event_id": "eid1",
            "sources": ["s1"],
            "evidence": [],
        }
    ]
    signals = emit_truth_signals(events)
    assert len(signals) == 1
    sig = signals[0]
    
    # Required fields
    assert "registry_reference_id" in sig
    assert "truth_level" in sig
    assert "conflict_flag" in sig
    
    # Field types
    assert isinstance(sig["truth_level"], int)
    assert isinstance(sig["conflict_flag"], bool)
    assert sig["registry_reference_id"] == "evt1"


def test_emit_truth_signals_preserves_event_id():
    """event_id from original event is preserved in signal"""
    events = [
        {
            "registry_reference_id": "r1",
            "event_id": "custom_event_123",
            "sources": [],
            "evidence": [],
        }
    ]
    signals = emit_truth_signals(events)
    assert signals[0]["event_id"] == "custom_event_123"


def test_emit_truth_signals_handles_missing_event_id():
    """event_id is optional; missing event_id becomes None or absent"""
    events = [
        {
            "registry_reference_id": "r1",
            "sources": [],
            "evidence": [],
        }
    ]
    signals = emit_truth_signals(events)
    # event_id should be None or not present
    assert signals[0].get("event_id") is None


def test_emit_truth_signals_no_mutation():
    """Original events are NOT mutated by emit_truth_signals"""
    events = [
        {
            "registry_reference_id": "r1",
            "sources": ["s1"],
            "evidence": [{"evidence_type": "direct"}],
            "metadata": "original",
        }
    ]
    events_copy = copy.deepcopy(events)
    
    # Call emit
    signals = emit_truth_signals(events)
    
    # Verify no mutation
    assert events == events_copy, "Original events were mutated!"
    assert "truth_level" not in events[0]
    assert "conflict_flag" not in events[0]


def test_emit_truth_signal_for_event_single():
    """Single event wrapper works correctly"""
    event = {
        "registry_reference_id": "single_evt",
        "sources": ["src1", "src2"],
        "evidence": [],
    }
    sig = emit_truth_signal_for_event(event)
    
    # Should be level 2 (multi-source)
    assert sig["truth_level"] == 2
    assert sig["registry_reference_id"] == "single_evt"
    assert isinstance(sig["conflict_flag"], bool)


# =============================================================================
# SCHEMA MUTATION TESTS
# =============================================================================

def test_classify_claim_no_input_mutation():
    """classify_claim does not modify input event dict"""
    event = {
        "sources": ["s1"],
        "evidence": [{"evidence_type": "report"}],
        "timestamp": "2024-01-01",
        "author": "john",
    }
    event_before = copy.deepcopy(event)
    event_id_before = id(event)
    
    result = classify_claim(event)
    
    # Verify no mutation
    assert event == event_before
    assert id(event) == event_id_before
    assert "truth_level" not in event
    assert result == 1


def test_detect_conflicts_no_input_mutation():
    """detect_conflicts does not modify input event dicts"""
    events = [
        {"registry_reference_id": "r1", "value": 10, "status": "open"},
        {"registry_reference_id": "r1", "value": 11, "status": "open"},
    ]
    events_before = copy.deepcopy(events)
    
    result = detect_conflicts(events)
    
    # Verify no mutation
    assert events == events_before
    for ev in events:
        assert "conflict_flag" not in ev


def test_classify_preserves_complex_schema():
    """classify_claim handles complex nested schemas without mutation"""
    event = {
        "registry_reference_id": "r1",
        "sources": ["s1", "s2"],
        "evidence": [
            {
                "evidence_type": "institutional",
                "metadata": {
                    "confidence": 0.95,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "source_rank": 5,
                }
            }
        ],
        "nested": {
            "deep": {
                "value": 123,
                "list": [1, 2, 3],
            }
        },
    }
    event_before = copy.deepcopy(event)
    
    result = classify_claim(event)
    
    # Verify no mutation
    assert event == event_before
    assert result == 3


# =============================================================================
# REGISTRY REFERENCE ID HANDLING TESTS
# =============================================================================

def test_conflict_detection_registry_id_grouping():
    """Conflict detection correctly groups by registry_reference_id"""
    events = [
        {"registry_reference_id": "alpha", "value": 1},
        {"registry_reference_id": "alpha", "value": 2},  # conflict
        {"registry_reference_id": "beta", "value": 3},
        {"registry_reference_id": "beta", "value": 3},  # no conflict
        {"registry_reference_id": "gamma", "value": 4},  # single event
    ]
    result = detect_conflicts(events)
    
    assert result["alpha"] is True  # Different values
    assert result["beta"] is False  # Same values
    assert result["gamma"] is False  # Single event, no pair to conflict


def test_conflict_detection_missing_registry_id():
    """Events without registry_reference_id get synthetic IDs"""
    events = [
        {"value": 10},  # index 0 -> __local__0
        {"value": 20},  # index 1 -> __local__1
        {"value": 30},  # index 2 -> __local__2
    ]
    result = detect_conflicts(events)
    
    # Each gets synthetic ID, only pairwise comparison within same id
    assert result["__local__0"] is False
    assert result["__local__1"] is False
    assert result["__local__2"] is False


def test_conflict_detection_mixed_registry_ids():
    """Mix of present and missing registry_reference_id"""
    events = [
        {"registry_reference_id": "r1", "value": 10},  # r1
        {"registry_reference_id": "r1", "value": 10},  # r1 (no conflict)
        {"value": 20},  # __local__2
        {"value": 30},  # __local__3
    ]
    result = detect_conflicts(events)
    
    assert "r1" in result
    assert "__local__2" in result
    assert "__local__3" in result
    assert result["r1"] is False


# =============================================================================
# FIELD PRESENCE & OPTIONALITY TESTS
# =============================================================================

def test_classify_sources_field_optional():
    """classify_claim works when 'sources' field is missing"""
    cases = [
        {},  # no sources, no evidence
        {"evidence": []},  # no sources
        {"sources": None, "evidence": []},  # None sources
    ]
    for case in cases:
        result = classify_claim(case)
        assert result == 0


def test_classify_evidence_field_optional():
    """classify_claim works when 'evidence' field is missing"""
    cases = [
        {},  # no sources, no evidence
        {"sources": ["s1"]},  # has sources, no evidence
        {"sources": ["s1"], "evidence": None},  # None evidence
    ]
    results = [classify_claim(c) for c in cases]
    assert results[0] == 0  # no sources
    assert results[1] == 1  # single source
    assert results[2] == 1  # single source


def test_conflict_registry_reference_id_optional():
    """detect_conflicts works without registry_reference_id"""
    events = [
        {"value": 10},
        {"value": 20},
    ]
    result = detect_conflicts(events)
    # Should have synthetic IDs
    assert "__local__0" in result
    assert "__local__1" in result


# =============================================================================
# OUTPUT CONTRACT TESTS
# =============================================================================

def test_truth_level_range_all_cases():
    """truth_level is always exactly int 0-4"""
    test_inputs = [
        {"sources": [], "evidence": []},
        {"sources": ["a"], "evidence": []},
        {"sources": ["a", "b"], "evidence": []},
        {"sources": [], "evidence": [{"evidence_type": "report"}]},
        {"sources": [], "evidence": [{"evidence_type": "report"}, {"evidence_type": "report"}]},
        {"sources": [], "evidence": [{"evidence_type": "institutional"}]},
        {"sources": [], "evidence": [{"evidence_type": "direct"}]},
    ]
    
    results = [classify_claim(case) for case in test_inputs]
    expected = [0, 1, 2, 1, 2, 3, 4]
    
    assert results == expected
    assert all(isinstance(r, int) for r in results)
    assert all(0 <= r <= 4 for r in results)


def test_conflict_flag_always_boolean():
    """conflict_flag is always exactly True or False (not truthy/falsy)"""
    events = [
        [{"registry_reference_id": "r1", "value": 10}],
        [
            {"registry_reference_id": "r1", "value": 10},
            {"registry_reference_id": "r1", "value": 11},
        ],
        [
            {"registry_reference_id": "r1", "status": "open"},
            {"registry_reference_id": "r1", "status": "closed"},
        ],
    ]
    
    for event_list in events:
        result = detect_conflicts(event_list)
        for rid, flag in result.items():
            assert isinstance(flag, bool), f"Expected bool, got {type(flag)}: {flag}"
            assert flag is True or flag is False


# =============================================================================
# INTEGRATION CONTRACT TESTS
# =============================================================================

def test_full_signal_pipeline():
    """Complete pipeline: input event -> truth signal with all fields"""
    input_event = {
        "registry_reference_id": "event_xyz",
        "event_id": "eid_123",
        "sources": ["bbc", "cnn"],
        "evidence": [
            {"evidence_type": "institutional"},
        ],
        "headline": "Breaking news",
        "timestamp": "2024-01-01T00:00:00Z",
    }
    
    # Single event signal
    signal = emit_truth_signal_for_event(input_event)
    
    # Verify signal contract
    assert signal["registry_reference_id"] == "event_xyz"
    assert signal["event_id"] == "eid_123"
    assert signal["truth_level"] == 3  # institutional
    assert signal["conflict_flag"] is False  # only one event
    
    # Verify input not mutated
    assert "truth_level" not in input_event
    assert "conflict_flag" not in input_event


def test_batch_signals_contract():
    """Batch signal pipeline maintains contract across multiple events"""
    events = [
        {
            "registry_reference_id": "batch_r1",
            "event_id": "batch_e1",
            "sources": ["s1"],
            "evidence": [],
        },
        {
            "registry_reference_id": "batch_r2",
            "event_id": "batch_e2",
            "sources": ["s2"],
            "evidence": [{"evidence_type": "direct"}],
        },
    ]
    
    signals = emit_truth_signals(events)
    
    assert len(signals) == 2
    
    # First signal
    assert signals[0]["registry_reference_id"] == "batch_r1"
    assert signals[0]["event_id"] == "batch_e1"
    assert signals[0]["truth_level"] == 1
    assert isinstance(signals[0]["conflict_flag"], bool)
    
    # Second signal
    assert signals[1]["registry_reference_id"] == "batch_r2"
    assert signals[1]["event_id"] == "batch_e2"
    assert signals[1]["truth_level"] == 4
    assert isinstance(signals[1]["conflict_flag"], bool)
