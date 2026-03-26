"""
Cross-Source Event Matching - Phase 3 of Truth Intelligence Layer.
Detects when multiple articles refer to the same event.
Uses entity overlap, location, and time proximity.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import hashlib
import datetime

# Time proximity thresholds (in hours) - defined at module level
SAME_DAY_THRESHOLD = 24
WITHIN_WEEK_THRESHOLD = 168  # 7 days

@dataclass
class EventMatch:
    """Represents a matched event group."""
    group_id: str
    canonical_event: Dict[str, Any]
    matched_events: List[Dict[str, Any]]
    match_score: float
    match_reasons: List[str]


class EventMatcher:
    """
    Matches events from different sources that refer to the same underlying event.

    Uses multiple signals:
    - Entity overlap (named entities, organizations)
    - Location proximity
    - Time proximity (within configurable window)
    - Semantic similarity (optional)
    """

    # Default weights for matching signals
    ENTITY_WEIGHT = 0.40
    LOCATION_WEIGHT = 0.30
    TIME_WEIGHT = 0.20
    SEMANTIC_WEIGHT = 0.10

    # Time proximity thresholds (in hours)
    SAME_DAY_THRESHOLD = 24
    WITHIN_WEEK_THRESHOLD = 168  # 7 days

    def __init__(self, time_window_hours: int = SAME_DAY_THRESHOLD):
        """
        Initialize EventMatcher.

        Args:
            time_window_hours: Maximum time difference for matching (default 24 hours)
        """
        self.time_window_hours = time_window_hours

    def match_events(
        self,
        events: List[Dict[str, Any]]
    ) -> List[EventMatch]:
        """
        Match events that refer to the same underlying event.

        Args:
            events: List of event dictionaries

        Returns:
            List of EventMatch objects, each containing matched events
        """
        if len(events) < 2:
            return []

        # Build match groups
        matched_indices = set()
        match_groups: List[EventMatch] = []

        for i, event in enumerate(events):
            if i in matched_indices:
                continue

            # Find matching events for this one
            group_indices = [i]
            group_events = [event]
            match_reasons = []

            for j, other_event in enumerate(events[i + 1:], start=i + 1):
                if j in matched_indices:
                    continue

                match_result = self._calculate_match_score(event, other_event)
                if match_result['match']:
                    group_indices.append(j)
                    group_events.append(other_event)
                    match_reasons.extend(match_result['reasons'])

            if len(group_events) > 1:
                # Mark all indices as matched
                for idx in group_indices:
                    matched_indices.add(idx)

                # Create canonical event (use most complete one)
                canonical = self._select_canonical_event(group_events)

                # Generate group ID
                group_id = self._generate_group_id(canonical)

                match_groups.append(EventMatch(
                    group_id=group_id,
                    canonical_event=canonical,
                    matched_events=group_events,
                    match_score=match_result['score'],
                    match_reasons=list(set(match_reasons))
                ))

        return match_groups

    def _calculate_match_score(
        self,
        event1: Dict[str, Any],
        event2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate match score between two events.

        Returns:
            Dict with 'match' (bool), 'score' (float), 'reasons' (list)
        """
        scores = []
        reasons = []

        # 1. Entity overlap check
        entity_score = self._calculate_entity_overlap(event1, event2)
        if entity_score > 0:
            scores.append(entity_score * self.ENTITY_WEIGHT)
            if entity_score >= 0.5:
                reasons.append("entity_overlap")

        # 2. Location proximity check
        location_score = self._calculate_location_score(event1, event2)
        if location_score > 0:
            scores.append(location_score * self.LOCATION_WEIGHT)
            if location_score >= 0.8:
                reasons.append("location_match")

        # 3. Time proximity check
        time_score = self._calculate_time_score(event1, event2)
        if time_score > 0:
            scores.append(time_score * self.TIME_WEIGHT)
            if time_score >= 0.8:
                reasons.append("time_proximity")

        # Calculate weighted total
        total_score = sum(scores) if scores else 0.0

        # Match threshold
        match = total_score >= 0.5 and len(reasons) >= 1

        return {
            'match': match,
            'score': round(total_score, 3),
            'reasons': reasons
        }

    def _calculate_entity_overlap(
        self,
        event1: Dict[str, Any],
        event2: Dict[str, Any]
    ) -> float:
        """
        Calculate entity overlap between two events.
        """
        entities1 = self._extract_entities(event1)
        entities2 = self._extract_entities(event2)

        if not entities1 or not entities2:
            return 0.0

        overlap = entities1 & entities2
        total = entities1 | entities2

        return len(overlap) / len(total) if total else 0.0

    def _extract_entities(self, event: Dict[str, Any]) -> set:
        """Extract named entities from event."""
        entities = set()

        # Extract from dedicated fields
        for field in ['entities', 'named_entities', 'people', 'organizations', 'topics']:
            if field in event:
                value = event[field]
                if isinstance(value, list):
                    entities.update(str(e).lower() for e in value)
                elif isinstance(value, str):
                    entities.update(e.lower() for e in value.split(','))

        # Extract from content if available
        content = event.get('content') or event.get('summary') or event.get('title', '')
        # Simple extraction - in production would use NER
        if content:
            words = content.split()
            # Filter short words and common stopwords
            stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of'}
            entities.update(w.lower() for w in words if len(w) > 3 and w.lower() not in stopwords)

        return entities

    def _calculate_location_score(
        self,
        event1: Dict[str, Any],
        event2: Dict[str, Any]
    ) -> float:
        """
        Calculate location proximity score.
        """
        loc1 = event1.get('location') or event1.get('place') or event1.get('region', '')
        loc2 = event2.get('location') or event2.get('place') or event2.get('region', '')

        if not loc1 or not loc2:
            # Check coordinates if available
            lat1 = event1.get('latitude') or event1.get('lat')
            lon1 = event1.get('longitude') or event1.get('lon')
            lat2 = event2.get('latitude') or event2.get('lat')
            lon2 = event2.get('longitude') or event2.get('lon')

            if all([lat1, lon1, lat2, lon2]):
                return self._coordinate_similarity(float(lat1), float(lon1), float(lat2), float(lon2))
            return 0.0

        # String-based location matching
        loc1_lower = str(loc1).lower().strip()
        loc2_lower = str(loc2).lower().strip()

        if loc1_lower == loc2_lower:
            return 1.0

        # Check if one contains the other
        if loc1_lower in loc2_lower or loc2_lower in loc1_lower:
            return 0.8

        return 0.0

    def _coordinate_similarity(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """
        Calculate similarity based on geographic distance.
        Returns 1.0 for same location, decreasing with distance.
        """
        # Haversine distance approximation
        import math
        dlat = abs(lat1 - lat2)
        dlon = abs(lon1 - lon2)

        # Simple Euclidean approximation (good enough for small distances)
        distance = math.sqrt(dlat**2 + dlon**2)

        # Convert to similarity (within 1 degree = high similarity)
        if distance < 0.1:  # ~10km
            return 1.0
        elif distance < 1.0:  # ~100km
            return 0.7
        elif distance < 5.0:  # ~500km
            return 0.3
        else:
            return 0.0

    def _calculate_time_score(
        self,
        event1: Dict[str, Any],
        event2: Dict[str, Any]
    ) -> float:
        """
        Calculate time proximity score.
        """
        import datetime

        ts1 = self._parse_timestamp(event1.get('timestamp') or event1.get('date') or event1.get('published_at'))
        ts2 = self._parse_timestamp(event2.get('timestamp') or event2.get('date') or event2.get('published_at'))

        if not ts1 or not ts2:
            return 0.0

        try:
            # Handle string timestamps
            if isinstance(ts1, str):
                ts1 = datetime.fromisoformat(ts1.replace('Z', '+00:00'))
            if isinstance(ts2, str):
                ts2 = datetime.fromisoformat(ts2.replace('Z', '+00:00'))

            diff_hours = abs((ts1 - ts2).total_seconds() / 3600)

            if diff_hours <= self.time_window_hours:
                return 1.0 - (diff_hours / self.time_window_hours)
            elif diff_hours <= WITHIN_WEEK_THRESHOLD:
                return 0.5
            else:
                return 0.0
        except (ValueError, TypeError):
            return 0.0

    def _parse_timestamp(self, ts: Any) -> Optional[datetime.datetime]:
        """Parse timestamp string to datetime."""
        if not ts:
            return None
        import datetime
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S%z",
        ]
        for fmt in formats:
            try:
                return datetime.datetime.strptime(str(ts), fmt)
            except ValueError:
                continue
        return None

    def _select_canonical_event(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the canonical event from a group (most complete one).
        """
        # Prefer events with more fields populated
        def completeness(event: Dict[str, Any]) -> int:
            important_fields = ['title', 'content', 'timestamp', 'location', 'entities', 'source_id']
            return sum(1 for f in important_fields if event.get(f))

        return max(events, key=completeness)

    def _generate_group_id(self, event: Dict[str, Any]) -> str:
        """
        Generate a stable group ID from canonical event.
        """
        # Use source_id + timestamp + location hash
        source = event.get('source_id', 'unknown')
        timestamp = event.get('timestamp', event.get('date', ''))
        location = event.get('location', event.get('region', ''))

        data = f"{source}:{timestamp}:{location}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


def match_events(events: List[Dict[str, Any]]) -> List[EventMatch]:
    """
    Convenience function for event matching.
    """
    matcher = EventMatcher()
    return matcher.match_events(events)


def get_matched_event_groups(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get matched event groups as dictionary output.

    Args:
        events: List of events to match

    Returns:
        Dictionary with matched groups information
    """
    matches = match_events(events)

    return {
        "total_events": len(events),
        "matched_groups": len(matches),
        "unmatched_events": len(events) - sum(len(m.matched_events) for m in matches),
        "groups": [
            {
                "group_id": m.group_id,
                "canonical_event": m.canonical_event,
                "event_count": len(m.matched_events),
                "match_score": m.match_score,
                "match_reasons": m.match_reasons
            }
            for m in matches
        ]
    }
