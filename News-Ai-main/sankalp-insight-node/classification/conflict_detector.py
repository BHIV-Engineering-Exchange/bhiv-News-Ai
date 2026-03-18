"""
Conflict Detection Engine for Samachar.
Evaluates structural contradictions for identical registry_reference_id.
"""

from typing import List, Dict, Any, Optional

def detect_conflicts(registry_id: str, events: List[Dict[str, Any]]) -> bool:
    """
    Evaluates a set of ingestion events sharing the same registry_reference_id
    for structural contradictions.
    
    Checks for:
    1. Contradictory factual statements: Differing 'status', 'outcome', or 'verified' values.
    2. Opposing claims: Opposite values for boolean attributes (e.g., 'is_active': True vs False).
    3. Incompatible numeric values: Differing values for 'amount', 'count', or 'score' for the same reference.
    4. Incompatible event timelines: Overlapping or non-sequential 'timestamp' or 'date' sequences for the same claim.
    
    If any contradiction is detected, conflict_flag = True.
    Conflict is only flagged, not resolved. Ambiguity is preserved for downstream systems.
    """
    if not events or len(events) < 2:
        return False

    # Filter events for the relevant registry_id
    relevant_events = [e for e in events if e.get('registry_reference_id') == registry_id]
    if len(relevant_events) < 2:
        return False

    # 1. Check status/outcome contradictions
    status_values = set()
    outcome_values = set()
    for event in relevant_events:
        if 'status' in event:
            status_values.add(str(event['status']).lower())
        if 'outcome' in event:
            outcome_values.add(str(event['outcome']).lower())

    if len(status_values) > 1 or len(outcome_values) > 1:
        return True

    # 2. Check opposing claims (boolean fields)
    for attr in ['is_active', 'is_verified', 'is_complete', 'is_truthful']:
        values = set()
        for event in relevant_events:
            if attr in event:
                values.add(event[attr])
        if len(values) > 1:
            return True

    # 3. Check numeric value incompatibilities
    for attr in ['amount', 'count', 'score', 'value']:
        values = set()
        for event in relevant_events:
            if attr in event:
                values.add(event[attr])
        if len(values) > 1:
            return True

    # 4. Check timeline sequence incompatibilities
    # If the same state is reached at different times without a transition, or if timestamps overlap
    # This is a simplified timeline check for structural integrity.
    # Note: In a real system, this would involve ordering by timestamp and checking valid transitions.
    # For now, we flag any event with the same timestamp but different IDs as a conflict.
    timestamps = {} # timestamp -> set of event_ids
    for event in relevant_events:
        ts = event.get('timestamp') or event.get('date')
        if ts:
            if ts not in timestamps:
                timestamps[ts] = set()
            timestamps[ts].add(event.get('event_id') or event.get('source_hash'))
            
    # If multiple distinct event_ids exist for the same exact timestamp, it's a structural conflict
    for ts, ids in timestamps.items():
        if len(ids) > 1:
            return True

    return False

def get_event_conflict_metadata(registry_id: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Wraps the conflict detector output for Samachar event ingestion.
    """
    return {
        "conflict_flag": detect_conflicts(registry_id, events)
    }
