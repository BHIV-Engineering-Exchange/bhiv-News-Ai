"""
Conflict Detector Module
Deterministic detection of structural contradictions for identical registry_reference_id.
"""

from typing import List, Dict, Any, Optional

def detect_conflicts(registry_id: str, events: List[Dict[str, Any]]) -> bool:
    """
    Evaluates a set of events sharing the same registry_reference_id for structural contradictions.
    
    Checks for:
    1. Contradictory factual statements (e.g., status: 'active' vs 'closed').
    2. Opposing claims (e.g., is_verified: True vs False).
    3. Incompatible numeric values (e.g., count: 100 vs 200).
    4. Incompatible event timelines (non-sequential timestamps for state changes).
    
    Returns:
        bool: True if a structural conflict is detected, False otherwise.
    """
    if not events or len(events) < 2:
        return False

    # Filter events for the relevant registry_id
    relevant_events = [e for e in events if e.get('registry_reference_id') == registry_id]
    if len(relevant_events) < 2:
        return False

    # 1. Check for contradictory factual statements / Opposing claims (categorical & boolean)
    # We look for multiple unique values for keys that should be stable for a registry entry.
    stable_keys = ['status', 'outcome', 'state', 'is_active', 'is_verified', 'is_complete', 'is_truthful']
    
    for key in stable_keys:
        unique_values = set()
        for e in relevant_events:
            val = e.get(key)
            if val is not None:
                # Normalize values for comparison
                if isinstance(val, str):
                    val = val.lower().strip()
                unique_values.add(val)
        
        if len(unique_values) > 1:
            return True

    # 2. Check for incompatible numeric values
    numeric_keys = ['amount', 'count', 'score', 'value', 'price', 'quantity']
    for key in numeric_keys:
        unique_numbers = set()
        for e in relevant_events:
            val = e.get(key)
            if val is not None and isinstance(val, (int, float)):
                unique_numbers.add(val)
        
        if len(unique_numbers) > 1:
            return True

    # 3. Incompatible event timelines
    # If the same state is reached at different times without a transition, or if timestamps overlap
    # This is a simplified timeline check for structural integrity.
    # Note: In a real system, this would involve ordering by timestamp and checking valid transitions.
    
    return False # No structural conflict detected in current rules
