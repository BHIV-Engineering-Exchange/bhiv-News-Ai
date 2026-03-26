"""
Truth Intelligence Layer for Samachar.
Deterministic truth classification, conflict detection, and source reliability scoring.
"""

from .truth_classifier import TruthLevel, classify_truth_level, get_event_truth_metadata
from .source_reliability import SourceReliabilityScorer, get_source_reliability_score, get_source_metadata, update_source_verification
from .event_matcher import EventMatcher, match_events, get_matched_event_groups, EventMatch
from .conflict_detector import ConflictDetector, detect_conflicts, get_event_conflict_metadata, ConflictType, ConflictRecord
from .truth_state_engine import TruthStateEngine, resolve_truth_state, TruthState, TruthConfidence
from .pipeline_integration import TruthIntelligenceLayer, TruthIntelligenceConfig, process_event_pipeline, get_event_truth, update_verification

__all__ = [
    # Truth Classifier
    "TruthLevel",
    "classify_truth_level",
    "get_event_truth_metadata",
    # Source Reliability
    "SourceReliabilityScorer",
    "get_source_reliability_score",
    "get_source_metadata",
    "update_source_verification",
    # Event Matcher
    "EventMatcher",
    "match_events",
    "get_matched_event_groups",
    "EventMatch",
    # Conflict Detector
    "ConflictDetector",
    "detect_conflicts",
    "get_event_conflict_metadata",
    "ConflictType",
    "ConflictRecord",
    # Truth State Engine
    "TruthStateEngine",
    "resolve_truth_state",
    "TruthState",
    "TruthConfidence",
    # Pipeline Integration
    "TruthIntelligenceLayer",
    "TruthIntelligenceConfig",
    "process_event_pipeline",
    "get_event_truth",
    "update_verification",
]
__version__ = "1.0.0"
