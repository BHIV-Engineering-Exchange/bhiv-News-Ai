"""
Pipeline Integration Module - Phase 6 of Truth Intelligence Layer.
Integrates truth intelligence components into the event extraction pipeline.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

from .truth_classifier import TruthLevel, classify_truth_level, get_event_truth_metadata
from .source_reliability import (
    SourceReliabilityScorer,
    get_source_reliability_score,
    get_source_metadata,
    update_source_verification
)
from .event_matcher import EventMatcher, match_events, get_matched_event_groups
from .conflict_detector import ConflictDetector, detect_conflicts, get_event_conflict_metadata
from .truth_state_engine import TruthStateEngine, resolve_truth_state


@dataclass
class TruthIntelligenceConfig:
    """Configuration for Truth Intelligence Layer."""
    enable_conflict_detection: bool = True
    enable_event_matching: bool = True
    enable_source_scoring: bool = True
    enable_truth_resolution: bool = True
    numeric_tolerance: float = 0.01
    event_matching_window_hours: int = 24


class TruthIntelligenceLayer:
    """
    Main entry point for the Truth Intelligence Layer.

    Integrates all truth intelligence components:
    - Truth Classification
    - Source Reliability Scoring
    - Event Matching
    - Conflict Detection
    - Truth State Resolution
    """

    def __init__(self, config: Optional[TruthIntelligenceConfig] = None):
        """
        Initialize Truth Intelligence Layer.

        Args:
            config: Optional configuration object
        """
        self.config = config or TruthIntelligenceConfig()
        self._source_scorer = SourceReliabilityScorer()
        self._conflict_detector = ConflictDetector(
            numeric_tolerance=self.config.numeric_tolerance
        )
        self._event_matcher = EventMatcher(
            time_window_hours=self.config.event_matching_window_hours
        )
        self._truth_engine = TruthStateEngine()

    def process_events(
        self,
        events: List[Dict[str, Any]],
        registry_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process events through the full Truth Intelligence pipeline.

        Args:
            events: List of events from Event Extraction Layer (Seeya)
            registry_id: Optional registry reference ID for grouping

        Returns:
            Events enriched with truth intelligence signals
        """
        enriched_events = []

        for event in events:
            enriched = self.process_single_event(event, events, registry_id)
            enriched_events.append(enriched)

        return enriched_events

    def process_single_event(
        self,
        event: Dict[str, Any],
        all_events: List[Dict[str, Any]],
        registry_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single event through truth intelligence.

        Args:
            event: The event to process
            all_events: All events (for conflict detection and matching)
            registry_id: Optional registry reference ID

        Returns:
            Event enriched with truth signals
        """
        truth_signals = self.get_truth_signals(event, all_events, registry_id)

        # Add truth signals to event
        enriched = {**event}
        enriched['truth_intelligence'] = truth_signals

        return enriched

    def get_truth_signals(
        self,
        event: Dict[str, Any],
        all_events: List[Dict[str, Any]],
        registry_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive truth signals for an event.

        Args:
            event: The event to analyze
            all_events: All events for correlation
            registry_id: Optional registry reference ID

        Returns:
            Dictionary with all truth signals
        """
        # Extract sources from event
        sources = event.get('sources', [])

        # 1. Truth Classification
        truth_metadata = get_event_truth_metadata(sources)

        # 2. Source Reliability
        source_reliability = {}
        if self.config.enable_source_scoring:
            for source in sources:
                sid = source.get('source_id') or source.get('source_hash', 'unknown')
                source_reliability[sid] = get_source_metadata(source, sid)

        # 3. Event Matching
        matched_groups = {}
        if self.config.enable_event_matching:
            # Match against other events
            other_events = [e for e in all_events if e != event]
            match_result = get_matched_event_groups([event] + other_events)
            matched_groups = match_result.get('groups', [])

        # 4. Conflict Detection
        conflict_metadata = {}
        if self.config.enable_conflict_detection:
            effective_registry_id = registry_id or event.get('registry_reference_id')
            if effective_registry_id:
                conflict_metadata = get_event_conflict_metadata(
                    effective_registry_id,
                    all_events
                )

        # 5. Truth State Resolution
        truth_state = {}
        if self.config.enable_truth_resolution:
            effective_registry_id = registry_id or event.get('registry_reference_id')
            truth_state = resolve_truth_state(
                sources,
                all_events,
                effective_registry_id
            )

        # Combine all signals
        return {
            "truth_classification": truth_metadata,
            "source_reliability": source_reliability,
            "event_matching": {
                "is_matched": len(matched_groups) > 0,
                "matched_groups": matched_groups
            },
            "conflict_detection": conflict_metadata,
            "truth_resolution": truth_state,
            "processing_timestamp": self._get_timestamp()
        }

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


def process_event_pipeline(
    events: List[Dict[str, Any]],
    registry_id: Optional[str] = None,
    config: Optional[TruthIntelligenceConfig] = None
) -> List[Dict[str, Any]]:
    """
    Process events through the Truth Intelligence pipeline.

    This is the main entry point for integrating with Seeya's Event Extraction Layer.

    Pipeline Flow:
    Event Extraction (Seeya)
           ↓
    Truth Intelligence Layer
           ↓
    Signal Generator
           ↓
         Bucket

    Args:
        events: Events from Seeya's Event Extraction
        registry_id: Optional registry reference ID
        config: Optional TruthIntelligenceConfig

    Returns:
        Events enriched with truth signals
    """
    layer = TruthIntelligenceLayer(config)
    return layer.process_events(events, registry_id)


# Convenience functions for direct access
def get_event_truth(event: Dict[str, Any], all_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get truth signals for a single event.

    Args:
        event: The event to analyze
        all_events: All events for correlation

    Returns:
        Truth signals dictionary
    """
    layer = TruthIntelligenceLayer()
    registry_id = event.get('registry_reference_id')
    return layer.get_truth_signals(event, all_events, registry_id)


def update_verification(source_id: str, verified: bool) -> None:
    """
    Update source verification status for future scoring.

    Args:
        source_id: Source identifier
        verified: Whether reports from this source were verified
    """
    update_source_verification(source_id, verified)
