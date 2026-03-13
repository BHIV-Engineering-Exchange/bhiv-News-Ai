import pytest
from truth_classifier import classify_truth_level, TruthLevel
from conflict_detector import detect_conflicts

# --- Truth Classifier Tests ---

def test_unverified_claim():
    sources = []
    assert classify_truth_level(sources) == TruthLevel.UNVERIFIED

def test_single_source():
    sources = [{"source_id": "bbc-001"}]
    assert classify_truth_level(sources) == TruthLevel.SINGLE_SOURCE

def test_multi_source():
    sources = [
        {"source_id": "bbc-001"},
        {"source_id": "reuters-001"}
    ]
    assert classify_truth_level(sources) == TruthLevel.CORROBORATED

def test_authoritative_source():
    sources = [
        {"source_id": "official-gov-001", "authority_level": 3}
    ]
    assert classify_truth_level(sources) == TruthLevel.AUTHORITATIVE

def test_primary_evidence():
    sources = [
        {"source_id": "leak-doc-001", "primary_evidence": True}
    ]
    assert classify_truth_level(sources) == TruthLevel.PRIMARY_EVIDENCE

def test_precedence_rules():
    # Primary evidence should trump authority level
    sources = [
        {"source_id": "source-1", "authority_level": 3},
        {"source_id": "source-2", "primary_evidence": True}
    ]
    assert classify_truth_level(sources) == TruthLevel.PRIMARY_EVIDENCE

# --- Conflict Detector Tests ---

def test_no_conflicts():
    registry_id = "REF-123"
    new_entry = {"status": "active", "count": 100}
    existing = [{"registry_reference_id": "REF-123", "status": "active", "count": 100}]
    assert detect_conflicts(registry_id, new_entry, existing) is False

def test_numeric_conflict():
    registry_id = "REF-123"
    new_entry = {"count": 200}
    existing = [{"registry_reference_id": "REF-123", "count": 100}]
    assert detect_conflicts(registry_id, new_entry, existing) is True

def test_categorical_conflict():
    registry_id = "REF-123"
    new_entry = {"status": "closed"}
    existing = [{"registry_reference_id": "REF-123", "status": "active"}]
    assert detect_conflicts(registry_id, new_entry, existing) is True

def test_boolean_conflict():
    registry_id = "REF-123"
    new_entry = {"verified": True}
    existing = [{"registry_reference_id": "REF-123", "verified": False}]
    assert detect_conflicts(registry_id, new_entry, existing) is True

def test_cross_registry_no_conflict():
    # Entries for different registry IDs should not conflict
    registry_id = "REF-123"
    new_entry = {"status": "closed"}
    existing = [{"registry_reference_id": "REF-456", "status": "active"}]
    assert detect_conflicts(registry_id, new_entry, existing) is False
