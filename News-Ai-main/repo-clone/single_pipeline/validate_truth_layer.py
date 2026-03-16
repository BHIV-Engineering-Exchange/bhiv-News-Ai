"""
Determinism Validation Script for Samachar Truth Layer.
Verifies identical outputs for identical inputs (replayability).
"""

import json
import hashlib
from truth_classifier import classify_truth_level
from conflict_detector import detect_conflicts

def generate_event_id(source_hash, registry_id, timestamp):
    """Simulates canonical event ID generation."""
    payload = f"{source_hash}:{registry_id}:{timestamp}"
    return hashlib.sha256(payload.encode()).hexdigest()

def run_validation():
    print("--- Starting Determinism Validation ---")
    
    # 1. Input Data
    source_metadata = {
        "source_hash": "HASH_ABC_123",
        "registry_reference_id": "REG_999",
        "timestamp": "2026-03-13T12:00:00Z",
        "is_institutional": True,
        "status": "verified",
        "amount": 5000
    }
    
    # 2. Run Ingestion Simulation 1
    event_1 = {
        "event_id": generate_event_id(source_metadata['source_hash'], source_metadata['registry_reference_id'], source_metadata['timestamp']),
        "truth_level": classify_truth_level([source_metadata]),
        "conflict_flag": detect_conflicts(source_metadata['registry_reference_id'], [source_metadata]),
        "registry_reference_id": source_metadata['registry_reference_id']
    }
    
    # 3. Run Ingestion Simulation 2 (Replay)
    event_2 = {
        "event_id": generate_event_id(source_metadata['source_hash'], source_metadata['registry_reference_id'], source_metadata['timestamp']),
        "truth_level": classify_truth_level([source_metadata]),
        "conflict_flag": detect_conflicts(source_metadata['registry_reference_id'], [source_metadata]),
        "registry_reference_id": source_metadata['registry_reference_id']
    }
    
    # 4. Assert Identity
    print(f"Event 1: {json.dumps(event_1, indent=2)}")
    print(f"Event 2: {json.dumps(event_2, indent=2)}")
    
    assert event_1 == event_2, "FAILED: Events are not identical on replay!"
    print("\n✅ PASSED: Identical inputs produced identical outputs.")

    # 5. Conflict Detection Proof
    print("\n--- Testing Conflict Detection ---")
    conflicting_source = source_metadata.copy()
    conflicting_source['amount'] = 10000 # Different amount for same registry
    
    events_for_conflict = [source_metadata, conflicting_source]
    conflict_flag = detect_conflicts("REG_999", events_for_conflict)
    
    print(f"Conflict Flag for incompatible numeric values: {conflict_flag}")
    assert conflict_flag is True, "FAILED: Conflict was not detected!"
    print("✅ PASSED: Conflict detected correctly.")

if __name__ == "__main__":
    run_validation()
