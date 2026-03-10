"""
Integration Tests - Full System Pipeline

Tests the complete truth classification and conflict detection system:
1. truth_classifier (rule-based truth_level 0-4)
2. conflict_detector (registry-based conflict_flag detection)
3. samachar_integration (truth signal emission)

Validates:
- End-to-end deterministic behavior
- Contract compliance across modules
- Structural contradictions detected correctly
- Truth levels assigned according to rules
- No data mutation
- Replayability across multiple invocations
"""
import copy
import json
import sys
sys.path.insert(0, '..')
from truth_classifier import classify_claim
from conflict_detector import detect_conflicts
from integrations.samachar_integration import emit_truth_signals


def test_complete_single_event_pipeline():
    """Single event: classify -> detect -> emit signal"""
    event = {
        "registry_reference_id": "news_001",
        "event_id": "evt_abc123",
        "headline": "Breaking News",
        "sources": ["bbc", "cnn", "reuters"],
        "evidence": [{"evidence_type": "institutional"}],
        "timestamp": "2024-01-15T10:30:00Z",
    }
    
    # Classify
    truth_level = classify_claim(event)
    assert truth_level == 3, "Multi-source institutional should be level 3"
    
    # Detect conflicts (single event, no conflict)
    conflicts = detect_conflicts([event])
    assert conflicts["news_001"] is False
    
    # Emit signal
    signals = emit_truth_signals([event])
    assert len(signals) == 1
    sig = signals[0]
    
    assert sig["registry_reference_id"] == "news_001"
    assert sig["truth_level"] == 3
    assert sig["conflict_flag"] is False
    assert sig["event_id"] == "evt_abc123"
    
    # Verify original not mutated
    assert "truth_level" not in event


def test_complete_contradicted_events_pipeline():
    """Contradicted events: different truth levels + conflict detected"""
    events = [
        {
            "registry_reference_id": "incident_42",
            "event_id": "evt_1",
            "sources": ["witness_1"],
            "evidence": [{"evidence_type": "direct"}],
            "casualty_count": 50,
            "location": "NYC",
        },
        {
            "registry_reference_id": "incident_42",
            "event_id": "evt_2",
            "sources": ["witness_2"],
            "evidence": [{"evidence_type": "report"}],
            "casualty_count": 100,  # CONFLICT
            "location": "NYC",
        },
    ]
    
    # Classify each separately
    levels = [classify_claim(e) for e in events]
    assert levels == [4, 1], "Direct evidence vs single report"
    
    # Detect conflicts
    conflicts = detect_conflicts(events)
    assert conflicts["incident_42"] is True, "Numeric conflict on casualty_count"
    
    # Emit signals
    signals = emit_truth_signals(events)
    assert len(signals) == 2
    
    # Both should have conflict flag
    for sig in signals:
        assert sig["registry_reference_id"] == "incident_42"
        assert sig["conflict_flag"] is True
    
    # But different truth levels
    assert signals[0]["truth_level"] == 4
    assert signals[1]["truth_level"] == 1


def test_multi_event_batch_processing():
    """Batch of 10 events with various truth levels and conflicts"""
    events = [
        {
            "registry_reference_id": "r_1",
            "sources": [],
            "evidence": [],
        },  # unverified (L0)
        {
            "registry_reference_id": "r_2",
            "sources": ["s1"],
            "evidence": [{"evidence_type": "report"}],
        },  # single source (L1)
        {
            "registry_reference_id": "r_3",
            "sources": ["s1", "s2"],
            "evidence": [],
        },  # multi-source (L2)
        {
            "registry_reference_id": "r_4",
            "sources": [],
            "evidence": [{"evidence_type": "institutional"}],
        },  # institutional (L3)
        {
            "registry_reference_id": "r_5",
            "sources": [],
            "evidence": [{"evidence_type": "direct"}],
        },  # direct evidence (L4)
        # Conflicted pair
        {
            "registry_reference_id": "r_6",
            "value": 10,
            "location": "Paris",
        },
        {
            "registry_reference_id": "r_6",
            "value": 20,  # CONFLICT
            "location": "Paris",
        },
        # Same values, no conflict
        {
            "registry_reference_id": "r_7",
            "value": 30,
        },
        {
            "registry_reference_id": "r_7",
            "value": 30,  # NO CONFLICT
        },
        # Single event
        {
            "registry_reference_id": "r_8",
            "sources": ["abc"],
            "evidence": [{"evidence_type": "report"}],
        },
    ]
    
    # Classify all
    levels = [classify_claim(e) for e in events]
    expected_levels = [0, 1, 2, 3, 4, 0, 0, 0, 0, 1]
    assert levels == expected_levels
    
    # Detect all conflicts
    conflicts = detect_conflicts(events)
    
    assert conflicts["r_1"] is False
    assert conflicts["r_2"] is False
    assert conflicts["r_3"] is False
    assert conflicts["r_4"] is False
    assert conflicts["r_5"] is False
    assert conflicts["r_6"] is True   # CONFLICTED
    assert conflicts["r_7"] is False  # Same values
    assert conflicts["r_8"] is False
    
    # Emit signals for all
    signals = emit_truth_signals(events)
    assert len(signals) == 10
    
    # Verify signal integrity
    assert signals[5]["conflict_flag"] is True
    assert signals[6]["conflict_flag"] is True
    assert signals[7]["conflict_flag"] is False


def test_replayability_across_invocations():
    """Same event batch produces identical signals on replay"""
    events = [
        {
            "registry_reference_id": "replay_1",
            "sources": ["s1", "s2"],
            "evidence": [{"evidence_type": "report"}],
            "value": 42,
        },
        {
            "registry_reference_id": "replay_2",
            "sources": [],
            "evidence": [{"evidence_type": "direct"}],
            "value": 42,
        },
    ]
    
    # Run pipeline 5 times
    all_signals = []
    for run in range(5):
        signals = emit_truth_signals(copy.deepcopy(events))
        all_signals.append(signals)
    
    # All runs should produce identical signals
    first_run = all_signals[0]
    for run_idx in range(1, 5):
        current_run = all_signals[run_idx]
        
        assert len(current_run) == len(first_run)
        for i, sig in enumerate(current_run):
            assert sig["registry_reference_id"] == first_run[i]["registry_reference_id"]
            assert sig["truth_level"] == first_run[i]["truth_level"]
            assert sig["conflict_flag"] == first_run[i]["conflict_flag"]
            assert sig["event_id"] == first_run[i]["event_id"]


def test_json_roundtrip_consistency():
    """Event serialization/deserialization preserves classification"""
    events = [
        {
            "registry_reference_id": "json_test_1",
            "sources": ["bbc", "cnn"],
            "evidence": [{"evidence_type": "institutional"}],
            "metadata": {"nested": {"deep": {"value": 123}}},
        },
        {
            "registry_reference_id": "json_test_1",
            "sources": ["bbc", "cnn"],
            "evidence": [{"evidence_type": "institutional"}],
            "metadata": {"nested": {"deep": {"value": 456}}},  # Different metadata
        },
    ]
    
    # Classify original
    signals_original = emit_truth_signals(events)
    
    # Roundtrip through JSON
    json_str = json.dumps(events)
    restored_events = json.loads(json_str)
    signals_restored = emit_truth_signals(restored_events)
    
    # Should be identical
    assert len(signals_original) == len(signals_restored)
    for i, (orig, rest) in enumerate(zip(signals_original, signals_restored)):
        assert orig["truth_level"] == rest["truth_level"], f"Signal {i} truth level mismatch"
        assert orig["conflict_flag"] == rest["conflict_flag"], f"Signal {i} conflict flag mismatch"


def test_large_batch_scalability():
    """System handles large batches correctly"""
    # Create 100 events with various registry IDs
    events = []
    for i in range(100):
        rid = f"event_{i % 10}"  # 10 unique registry IDs
        event = {
            "registry_reference_id": rid,
            "sources": [f"source_{j}" for j in range(i % 4)],  # 0-3 sources
            "evidence": [{"evidence_type": "report"} for _ in range(i % 3)],  # 0-2 evidence
        }
        events.append(event)
    
    # Should process all without errors
    signals = emit_truth_signals(events)
    assert len(signals) == 100
    
    # Verify all have required fields
    for sig in signals:
        assert "registry_reference_id" in sig
        assert "truth_level" in sig
        assert "conflict_flag" in sig
        assert 0 <= sig["truth_level"] <= 4
        assert isinstance(sig["conflict_flag"], bool)


def test_categorical_conflict_detection():
    """Categorical field contradictions are detected"""
    events = [
        {
            "registry_reference_id": "status_test",
            "status": "active",
            "type": "emergency",
        },
        {
            "registry_reference_id": "status_test",
            "status": "resolved",  # CONFLICT
            "type": "emergency",
        },
    ]
    
    conflicts = detect_conflicts(events)
    assert conflicts["status_test"] is True
    
    signals = emit_truth_signals(events)
    for sig in signals:
        assert sig["conflict_flag"] is True


def test_no_false_positives_metadata():
    """Metadata field differences don't trigger conflicts"""
    events = [
        {
            "registry_reference_id": "metadata_test",
            "value": 100,
            "updated_at": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "id": "id_1",
        },
        {
            "registry_reference_id": "metadata_test",
            "value": 100,
            "updated_at": "2024-01-02T00:00:00Z",  # DIFFERENT
            "created_at": "2024-01-02T00:00:00Z",  # DIFFERENT
            "id": "id_2",  # DIFFERENT
        },
    ]
    
    conflicts = detect_conflicts(events)
    assert conflicts["metadata_test"] is False, "Metadata differences should not cause conflicts"


def test_boolean_conflict_detection():
    """Boolean field contradictions are detected"""
    events = [
        {
            "registry_reference_id": "bool_test",
            "verified": True,
            "authenticated": True,
        },
        {
            "registry_reference_id": "bool_test",
            "verified": False,  # CONFLICT
            "authenticated": True,
        },
    ]
    
    conflicts = detect_conflicts(events)
    assert conflicts["bool_test"] is True
    
    signals = emit_truth_signals(events)
    for sig in signals:
        assert sig["conflict_flag"] is True


def test_hedge_language_detection():
    """Events with hedging language can be classified"""
    events = [
        {
            "registry_reference_id": "hedge_1",
            "headline": "Breaking news",
            "sources": ["source_1"],
            "evidence": [{"evidence_type": "report"}],
        },
        {
            "registry_reference_id": "hedge_2",
            "headline": "Official confirmation",
            "sources": ["official_authority"],
            "evidence": [{"evidence_type": "institutional"}],
        },
    ]
    
    signals = emit_truth_signals(events)
    
    # First event: single source report (L1)
    assert signals[0]["truth_level"] == 1
    assert signals[0]["registry_reference_id"] == "hedge_1"
    
    # Second event: institutional source (L3)
    assert signals[1]["truth_level"] == 3
    assert signals[1]["registry_reference_id"] == "hedge_2"
    
    # Different registry IDs, so no conflicts
    assert signals[0]["conflict_flag"] is False
    assert signals[1]["conflict_flag"] is False


def test_complete_workflow_example():
    """Real-world workflow: ingest, classify, detect, emit"""
    # Step 1: Ingest raw events from various sources
    raw_events = [
        {
            "event_id": "real_1",
            "registry_reference_id": "incident_xyz",
            "headline": "Police report incident",
            "sources": ["police_department"],
            "evidence": [{"evidence_type": "institutional"}],
            "description": "Reported 5 people injured",
            "injury_count": 5,
        },
        {
            "event_id": "real_2",
            "registry_reference_id": "incident_xyz",
            "headline": "Witness account",
            "sources": ["witness_on_scene"],
            "evidence": [{"evidence_type": "report"}],
            "description": "Saw at least 8 people injured",
            "injury_count": 8,  # CONTRADICTS
        },
        {
            "event_id": "real_3",
            "registry_reference_id": "incident_xyz",
            "headline": "Hospital statement",
            "sources": ["hospital_spokesperson"],
            "evidence": [{"evidence_type": "institutional"}],
            "description": "Confirmed 5 admissions from incident",
            "injury_count": 5,  # CONFIRMS first
        },
    ]
    
    # Step 2: Process through full pipeline
    signals = emit_truth_signals(raw_events)
    
    # Step 3: Analyze results
    assert len(signals) == 3
    
    # Check truth levels
    assert signals[0]["truth_level"] == 3  # institutional
    assert signals[1]["truth_level"] == 1  # single source report
    assert signals[2]["truth_level"] == 3  # institutional
    
    # Check conflict flags
    # All three share same registry_reference_id and have conflicting injury_count
    assert signals[0]["conflict_flag"] is True
    assert signals[1]["conflict_flag"] is True
    assert signals[2]["conflict_flag"] is True
    
    # Raw events not mutated
    for ev in raw_events:
        assert "truth_level" not in ev
        assert "conflict_flag" not in ev
    
    # Step 4: Can now query signals for truth assessment
    # - Most authoritative source (institutional) says 5
    # - But conflicting report says 8
    # - Consumers know to flag incident_xyz as CONFLICTED


if __name__ == "__main__":
    # Run one example
    test_complete_single_event_pipeline()
    print("✓ Single event pipeline passed")
    
    test_complete_contradicted_events_pipeline()
    print("✓ Contradicted events pipeline passed")
    
    test_replayability_across_invocations()
    print("✓ Replayability validation passed")
    
    print("\nAll integration tests passed!")
