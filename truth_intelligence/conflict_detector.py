"""
Conflict Detection Engine - Phase 4 of Truth Intelligence Layer.
Detects structural contradictions between events sharing the same registry_reference_id.
Extends the existing conflict_detector.py with numeric contradictions,
policy contradictions, and timeline inconsistencies.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ConflictType(Enum):
    """Types of conflicts that can be detected."""
    FACTUAL_CONTRADICTION = "factual_contradiction"
    OPPOSING_CLAIM = "opposing_claim"
    NUMERIC_INCOMPATIBILITY = "numeric_incompatibility"
    TIMELINE_INCONSISTENCY = "timeline_inconsistency"
    POLICY_CONTRADICTION = "policy_contradiction"
    SEMANTIC_CONTRADICTION = "semantic_contradiction"

# Fields monitored for each conflict type
FACTUAL_FIELDS = ['status', 'outcome', 'verified', 'result', 'decision']
BOOLEAN_FIELDS = ['is_active', 'is_verified', 'is_complete', 'is_truthful', 'confirmed', 'denied']
NUMERIC_FIELDS = ['amount', 'count', 'score', 'value', 'percentage', 'rate', 'population', 'price']
TIMESTAMP_FIELDS = ['timestamp', 'date', 'published_at', 'created_at', 'event_time']
POLICY_FIELDS = ['policy', 'stance', 'position', 'recommendation', 'guideline']
SEMANTIC_FIELDS = ['prediction', 'forecast', 'outlook', 'expectation']

@dataclass
class ConflictRecord:
    """Record of detected conflict."""
    conflict_type: ConflictType
    field: str
    conflicting_values: List[Any]
    conflicting_event_ids: List[str]


class ConflictDetector:
    """
    Detects conflicts between events sharing the same registry_reference_id.

    Conflict Types:
    1. Factual Contradiction: Different status/outcome values
    2. Opposing Claim: Conflicting boolean values
    3. Numeric Incompatibility: Different numeric values for same attribute
    4. Timeline Inconsistency: Same event at different times
    5. Policy Contradiction: Different policy positions
    6. Semantic Contradiction: Opposing predictions/forecasts
    """

    # Threshold for semantic contradiction detection
    SEMANTIC_CONTRADICTION_PAIRS = {
        ("normal", "below_normal"): True,
        ("above_normal", "below_normal"): True,
        ("increase", "decrease"): True,
        ("growth", "contraction"): True,
        ("positive", "negative"): True,
        ("likely", "unlikely"): True,
        ("expected", "unexpected"): True,
        ("confirmed", "denied"): True,
        ("support", "oppose"): True,
        ("agree", "disagree"): True,
        ("accept", "reject"): True,
        ("propose", "cancel"): True,
    }

    def __init__(self, numeric_tolerance: float = 0.01):
        """
        Initialize ConflictDetector.

        Args:
            numeric_tolerance: Tolerance for numeric comparison (default 1%)
        """
        self.numeric_tolerance = numeric_tolerance
        self._conflict_history: List[ConflictRecord] = []

    def detect_conflicts(
        self,
        registry_id: str,
        events: List[Dict[str, Any]]
    ) -> bool:
        """
        Detect if any conflicts exist among events for the same registry_id.

        Args:
            registry_id: The canonical registry reference ID
            events: List of events to check

        Returns:
            True if conflict detected, False otherwise
        """
        # Filter events for the relevant registry_id
        relevant_events = [e for e in events if e.get('registry_reference_id') == registry_id]

        if len(relevant_events) < 2:
            return False

        # Check each conflict type
        conflict_checks = [
            self._check_factual_contradictions(relevant_events),
            self._check_opposing_claims(relevant_events),
            self._check_numeric_incompatibilities(relevant_events),
            self._check_timeline_inconsistencies(relevant_events),
            self._check_policy_contradictions(relevant_events),
            self._check_semantic_contradictions(relevant_events),
        ]

        return any(conflict_checks)

    def detect_conflicts_with_details(
        self,
        registry_id: str,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect conflicts and return detailed information.

        Returns:
            Dictionary with conflict_flag, conflict_types, and conflicting_events
        """
        relevant_events = [e for e in events if e.get('registry_reference_id') == registry_id]

        if len(relevant_events) < 2:
            return {
                "conflict_flag": False,
                "conflict_types": [],
                "conflicting_fields": [],
                "conflicting_event_count": 0
            }

        conflicts: List[ConflictRecord] = []

        # Run all conflict checks
        conflicts.extend(self._get_factual_contradictions(relevant_events))
        conflicts.extend(self._get_opposing_claims(relevant_events))
        conflicts.extend(self._get_numeric_incompatibilities(relevant_events))
        conflicts.extend(self._get_timeline_inconsistencies(relevant_events))
        conflicts.extend(self._get_policy_contradictions(relevant_events))
        conflicts.extend(self._get_semantic_contradictions(relevant_events))

        return {
            "conflict_flag": len(conflicts) > 0,
            "conflict_types": list(set(c.conflict_type.value for c in conflicts)),
            "conflicting_fields": list(set(c.field for c in conflicts)),
            "conflict_count": len(conflicts),
            "conflicting_event_count": len(set(
                eid for c in conflicts for eid in c.conflicting_event_ids
            ))
        }

    def _check_factual_contradictions(self, events: List[Dict[str, Any]]) -> bool:
        """Check for contradictory factual statements."""
        return len(self._get_factual_contradictions(events)) > 0

    def _get_factual_contradictions(self, events: List[Dict[str, Any]]) -> List[ConflictRecord]:
        """Get detailed factual contradictions."""
        contradictions = []
        for field in FACTUAL_FIELDS:
            values = {}
            for event in events:
                if field in event:
                    val = str(event[field]).lower()
                    if val not in values:
                        values[val] = []
                    values[val].append(event.get('event_id') or event.get('source_hash', 'unknown'))

            if len(values) > 1:
                contradictions.append(ConflictRecord(
                    conflict_type=ConflictType.FACTUAL_CONTRADICTION,
                    field=field,
                    conflicting_values=list(values.keys()),
                    conflicting_event_ids=[eid for eids in values.values() for eid in eids]
                ))
        return contradictions

    def _check_opposing_claims(self, events: List[Dict[str, Any]]) -> bool:
        """Check for opposing boolean claims."""
        return len(self._get_opposing_claims(events)) > 0

    def _get_opposing_claims(self, events: List[Dict[str, Any]]) -> List[ConflictRecord]:
        """Get detailed opposing claims."""
        contradictions = []
        for field in BOOLEAN_FIELDS:
            values = set()
            event_ids = []
            for event in events:
                if field in event:
                    values.add(event[field])
                    event_ids.append(event.get('event_id') or event.get('source_hash', 'unknown'))

            if len(values) > 1:
                # Check for actual opposition (True vs False)
                if True in values and False in values:
                    contradictions.append(ConflictRecord(
                        conflict_type=ConflictType.OPPOSING_CLAIM,
                        field=field,
                        conflicting_values=list(values),
                        conflicting_event_ids=event_ids
                    ))
        return contradictions

    def _check_numeric_incompatibilities(self, events: List[Dict[str, Any]]) -> bool:
        """Check for incompatible numeric values."""
        return len(self._get_numeric_incompatibilities(events)) > 0

    def _get_numeric_incompatibilities(self, events: List[Dict[str, Any]]) -> List[ConflictRecord]:
        """Get detailed numeric incompatibilities."""
        contradictions = []
        for field in NUMERIC_FIELDS:
            numeric_values: List[Tuple[Any, str]] = []
            for event in events:
                if field in event:
                    try:
                        val = float(event[field])
                        eid = event.get('event_id') or event.get('source_hash', 'unknown')
                        numeric_values.append((val, eid))
                    except (ValueError, TypeError):
                        continue

            if len(numeric_values) > 1:
                # Check if values are significantly different
                vals = [v[0] for v in numeric_values]
                min_val, max_val = min(vals), max(vals)

                # Check if difference exceeds tolerance
                if max_val != 0:
                    relative_diff = (max_val - min_val) / abs(max_val)
                    if relative_diff > self.numeric_tolerance:
                        contradictions.append(ConflictRecord(
                            conflict_type=ConflictType.NUMERIC_INCOMPATIBILITY,
                            field=field,
                            conflicting_values=[v[0] for v in numeric_values],
                            conflicting_event_ids=[v[1] for v in numeric_values]
                        ))
        return contradictions

    def _check_timeline_inconsistencies(self, events: List[Dict[str, Any]]) -> bool:
        """Check for timeline inconsistencies."""
        return len(self._get_timeline_inconsistencies(events)) > 0

    def _get_timeline_inconsistencies(self, events: List[Dict[str, Any]]) -> List[ConflictRecord]:
        """Get detailed timeline inconsistencies."""
        import datetime

        inconsistencies = []
        timestamps_by_id: Dict[str, List[datetime.datetime]] = {}

        for event in events:
            eid = event.get('event_id') or event.get('source_hash', 'unknown')
            for field in TIMESTAMP_FIELDS:
                ts = event.get(field)
                if ts:
                    try:
                        if isinstance(ts, str):
                            parsed = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        else:
                            parsed = ts

                        if eid not in timestamps_by_id:
                            timestamps_by_id[eid] = []
                        timestamps_by_id[eid].append(parsed)
                    except (ValueError, TypeError):
                        continue

        # Check for same event_id with different timestamps
        for eid, timestamps in timestamps_by_id.items():
            if len(timestamps) > 1:
                unique_times = set(timestamps)
                if len(unique_times) > 1:
                    inconsistencies.append(ConflictRecord(
                        conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
                        field='timestamp',
                        conflicting_values=[str(t) for t in unique_times],
                        conflicting_event_ids=[eid]
                    ))

        return inconsistencies

    def _check_policy_contradictions(self, events: List[Dict[str, Any]]) -> bool:
        """Check for policy contradictions."""
        return len(self._get_policy_contradictions(events)) > 0

    def _get_policy_contradictions(self, events: List[Dict[str, Any]]) -> List[ConflictRecord]:
        """Get detailed policy contradictions."""
        contradictions = []
        for field in POLICY_FIELDS:
            policies: Dict[str, List[str]] = {}
            for event in events:
                if field in event:
                    val = str(event[field]).lower()
                    if val not in policies:
                        policies[val] = []
                    policies[val].append(event.get('event_id') or event.get('source_hash', 'unknown'))

            if len(policies) > 1:
                contradictions.append(ConflictRecord(
                    conflict_type=ConflictType.POLICY_CONTRADICTION,
                    field=field,
                    conflicting_values=list(policies.keys()),
                    conflicting_event_ids=[eid for eids in policies.values() for eid in eids]
                ))
        return contradictions

    def _check_semantic_contradictions(self, events: List[Dict[str, Any]]) -> bool:
        """Check for semantic contradictions (opposing predictions/forecasts)."""
        return len(self._get_semantic_contradictions(events)) > 0

    def _get_semantic_contradictions(self, events: List[Dict[str, Any]]) -> List[ConflictRecord]:
        """Get detailed semantic contradictions."""
        contradictions = []
        for field in SEMANTIC_FIELDS:
            values: Dict[str, List[str]] = {}
            for event in events:
                if field in event:
                    val = str(event[field]).lower()
                    if val not in values:
                        values[val] = []
                    values[val].append(event.get('event_id') or event.get('source_hash', 'unknown'))

            # Check for opposing pairs
            value_list = list(values.keys())
            for i, v1 in enumerate(value_list):
                for v2 in value_list[i + 1:]:
                    if self._are_opposing_terms(v1, v2):
                        contradictions.append(ConflictRecord(
                            conflict_type=ConflictType.SEMANTIC_CONTRADICTION,
                            field=field,
                            conflicting_values=[v1, v2],
                            conflicting_event_ids=values[v1] + values[v2]
                        ))
        return contradictions

    def _are_opposing_terms(self, term1: str, term2: str) -> bool:
        """Check if two terms are semantically opposing."""
        pair = (term1.strip(), term2.strip())
        reverse_pair = (term2.strip(), term1.strip())

        # Check predefined pairs
        if pair in self.SEMANTIC_CONTRADICTION_PAIRS:
            return True
        if reverse_pair in self.SEMANTIC_CONTRADICTION_PAIRS:
            return True

        # Check for direct negation
        negation_prefixes = ['not_', 'non_', 'un', 'anti', 'de', 'dis']
        for prefix in negation_prefixes:
            if term1.startswith(prefix) and term1[len(prefix):] == term2:
                return True
            if term2.startswith(prefix) and term2[len(prefix):] == term1:
                return True

        return False

    def get_conflict_history(self) -> List[Dict[str, Any]]:
        """Get history of detected conflicts."""
        return [
            {
                "type": c.conflict_type.value,
                "field": c.field,
                "values": c.conflicting_values,
                "event_ids": c.conflicting_event_ids
            }
            for c in self._conflict_history
        ]


def detect_conflicts(
    registry_id: str,
    events: List[Dict[str, Any]]
) -> bool:
    """
    Convenience function to detect conflicts.

    Args:
        registry_id: Registry reference ID
        events: List of events to check

    Returns:
        True if conflict detected
    """
    detector = ConflictDetector()
    return detector.detect_conflicts(registry_id, events)


def get_event_conflict_metadata(
    registry_id: str,
    events: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Get conflict metadata for event ingestion.

    Args:
        registry_id: Registry reference ID
        events: List of events to check

    Returns:
        Dictionary with conflict metadata
    """
    detector = ConflictDetector()
    details = detector.detect_conflicts_with_details(registry_id, events)

    return {
        "conflict_flag": details["conflict_flag"],
        "conflict_types": details["conflict_types"],
        "conflicting_fields": details["conflicting_fields"]
    }
