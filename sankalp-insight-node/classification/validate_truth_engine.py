"""
Determinism Validation Script for Truth Engine.
Verifies identical outputs for identical inputs.
"""

import hashlib
import json
from truth_classifier import classify_truth_level
from conflict_detector import detect_conflicts

def generate_event_id(source_hash: str, registry_id: str, timestamp: str) -> str:
    """Canonical event_id generation."""
    data = f"{source_hash}:{registry_id}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()

def run_validation():
    # Input data
    source_data = {
        "source_hash": "SOURCE_HASH_001",
        "registry_reference_id": "REGISTRY_ID_001",
        "timestamp": "2026-03-18T10:00:00Z",
        "is_institutional": True,
        "status": "verified"
    }
    
    # Simulate first ingestion
    event_1 = {
        "event_id": generate_event_id(source_data["source_hash"], source_data["registry_reference_id"], source_data["timestamp"]),
        "source_hash": source_data["source_hash"],
        "truth_level": classify_truth_level([source_data]),
        "conflict_flag": detect_conflicts(source_data["registry_reference_id"], [source_data]),
        "registry_reference_id": source_data["registry_reference_id"]
    }
    
    # Simulate second ingestion with identical source
    event_2 = {
        "event_id": generate_event_id(source_data["source_hash"], source_data["registry_reference_id"], source_data["timestamp"]),
        "source_hash": source_data["source_hash"],
        "truth_level": classify_truth_level([source_data]),
        "conflict_flag": detect_conflicts(source_data["registry_reference_id"], [source_data]),
        "registry_reference_id": source_data["registry_reference_id"]
    }
    
    # Comparison results
    print(f"Event 1: {json.dumps(event_1, indent=2)}")
    print(f"Event 2: {json.dumps(event_2, indent=2)}")
    
    assert event_1["event_id"] == event_2["event_id"]
    assert event_1["source_hash"] == event_2["source_hash"]
    assert event_1["truth_level"] == event_2["truth_level"]
    assert event_1["conflict_flag"] == event_2["conflict_flag"]
    assert event_1["registry_reference_id"] == event_2["registry_reference_id"]
    
    print("\n✅ Determinism Validation Passed: Identical inputs produced identical outputs.")

if __name__ == "__main__":
    run_validation()
