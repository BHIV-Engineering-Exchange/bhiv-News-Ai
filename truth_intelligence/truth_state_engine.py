"""
Truth State Resolver - Phase 5 of Truth Intelligence Layer.
Determines final truth state by combining corroboration and conflict signals.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .truth_classifier import TruthLevel, classify_truth_level
from .source_reliability import SourceReliabilityScorer, get_source_reliability_score
from .conflict_detector import ConflictDetector, detect_conflicts


class TruthConfidence(Enum):
    """Truth confidence levels."""
    VERY_HIGH = "VERY_HIGH"      # >= 0.90
    HIGH = "HIGH"                # >= 0.75
    MEDIUM = "MEDIUM"            # >= 0.50
    LOW = "LOW"                  # >= 0.25
    VERY_LOW = "VERY_LOW"        # < 0.25


@dataclass
class TruthState:
    """Final truth state output."""
    truth_level: int
    conflict_flag: bool
    confidence_score: float
    confidence_tier: str
    corroborating_sources: int
    conflicting_sources: int
    source_reliability_avg: float
    truth_signals: Dict[str, Any]


class TruthStateEngine:
    """
    Resolves final truth state by combining:
    - Source corroboration count
    - Conflict detection results
    - Source reliability scores
    - Truth classification level
    """

    # Confidence thresholds
    CONFIDENCE_VERY_HIGH = 0.90
    CONFIDENCE_HIGH = 0.75
    CONFIDENCE_MEDIUM = 0.50
    CONFIDENCE_LOW = 0.25

    # Corroboration weights
    CORROBORATION_BOOST = 0.10      # Per corroborating source
    CONFLICT_PENALTY = 0.30         # When conflict detected
    RELIABILITY_WEIGHT = 0.25       # Weight for average source reliability

    def __init__(self):
        self._source_scorer = SourceReliabilityScorer()
        self._conflict_detector = ConflictDetector()

    def resolve_truth_state(
        self,
        sources: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        registry_id: Optional[str] = None
    ) -> TruthState:
        """
        Resolve the final truth state for an event.

        Args:
            sources: List of source metadata dictionaries
            events: List of event dictionaries (for conflict detection)
            registry_id: Optional registry reference ID for conflict detection

        Returns:
            TruthState with all truth signals
        """
        # 1. Classify truth level
        truth_level = classify_truth_level(sources)

        # 2. Calculate source reliability scores
        source_scores = [get_source_reliability_score(s) for s in sources]
        avg_reliability = sum(source_scores) / len(source_scores) if source_scores else 0.0

        # 3. Detect conflicts
        conflict_detected = False
        conflict_types: List[str] = []
        if registry_id and events:
            conflict_detected = self._conflict_detector.detect_conflicts(registry_id, events)
            if conflict_detected:
                details = self._conflict_detector.detect_conflicts_with_details(registry_id, events)
                conflict_types = details.get('conflict_types', [])

        # 4. Count corroborating and conflicting sources
        corroborating, conflicting = self._count_source_alignment(sources, events, registry_id)

        # 5. Calculate confidence score
        confidence_score = self._calculate_confidence(
            truth_level=truth_level,
            source_count=len(sources),
            avg_reliability=avg_reliability,
            conflict_detected=conflict_detected,
            corroborating=corroborating,
            conflicting=conflicting
        )

        # 6. Determine confidence tier
        confidence_tier = self._get_confidence_tier(confidence_score)

        # 7. Build truth signals
        truth_signals = self._build_truth_signals(
            sources=sources,
            source_scores=source_scores,
            truth_level=truth_level,
            conflict_detected=conflict_detected,
            conflict_types=conflict_types,
            corroborating=corroborating,
            conflicting=conflicting,
            registry_id=registry_id
        )

        return TruthState(
            truth_level=truth_level,
            conflict_flag=conflict_detected,
            confidence_score=confidence_score,
            confidence_tier=confidence_tier,
            corroborating_sources=corroborating,
            conflicting_sources=conflicting,
            source_reliability_avg=round(avg_reliability, 3),
            truth_signals=truth_signals
        )

    def _count_source_alignment(
        self,
        sources: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        registry_id: Optional[str]
    ) -> Tuple[int, int]:
        """
        Count corroborating vs conflicting sources.

        A source is corroborating if its claim aligns with the majority.
        A source is conflicting if it contradicts the majority.
        """
        if not sources or len(sources) < 2:
            return len(sources), 0

        # Extract claims from events
        claims = []
        for event in events:
            if registry_id and event.get('registry_reference_id') != registry_id:
                continue
            # Extract key claim fields
            claim = self._extract_claim(event)
            if claim:
                claims.append(claim)

        if not claims:
            return len(sources), 0

        # Count claim frequencies
        claim_counts: Dict[str, int] = {}
        for claim in claims:
            claim_counts[claim] = claim_counts.get(claim, 0) + 1

        if not claim_counts:
            return len(sources), 0

        # Find majority claim
        majority_claim = max(claim_counts, key=claim_counts.get)

        # Count corroborating and conflicting
        corroborating = 0
        conflicting = 0

        for i, event in enumerate(events):
            if registry_id and event.get('registry_reference_id') != registry_id:
                continue
            claim = self._extract_claim(event)
            if claim == majority_claim:
                corroborating += 1
            else:
                conflicting += 1

        return corroborating, conflicting

    def _extract_claim(self, event: Dict[str, Any]) -> Optional[str]:
        """Extract a normalized claim from an event."""
        # Use status/outcome as the claim identifier
        status = event.get('status', '')
        outcome = event.get('outcome', '')
        prediction = event.get('prediction', '')

        if status:
            return f"status:{str(status).lower()}"
        if outcome:
            return f"outcome:{str(outcome).lower()}"
        if prediction:
            return f"prediction:{str(prediction).lower()}"

        return None

    def _calculate_confidence(
        self,
        truth_level: int,
        source_count: int,
        avg_reliability: float,
        conflict_detected: bool,
        corroborating: int,
        conflicting: int
    ) -> float:
        """
        Calculate final confidence score.

        Formula:
        - Base score from truth level (0-1 normalized from 0-4)
        - Source count bonus (up to +0.15 for multiple sources)
        - Reliability bonus (weighted contribution)
        - Corroboration bonus
        - Conflict penalty
        """
        # Base score from truth level
        base_score = truth_level / 4.0

        # Source count bonus
        source_bonus = min((source_count - 1) * 0.05, 0.15) if source_count > 1 else 0.0

        # Reliability contribution
        reliability_contribution = avg_reliability * self.RELIABILITY_WEIGHT

        # Corroboration bonus
        if corroborating > 0 and conflicting == 0:
            corroboration_bonus = min(corroborating * self.CORROBORATION_BOOST, 0.20)
        else:
            corroboration_bonus = 0.0

        # Conflict penalty
        if conflict_detected:
            conflict_penalty = self.CONFLICT_PENALTY
        else:
            conflict_penalty = 0.0

        # Calculate final score
        confidence = (
            base_score * 0.40 +
            source_bonus +
            reliability_contribution +
            corroboration_bonus -
            conflict_penalty
        )

        # Clamp to [0, 1]
        return max(0.0, min(1.0, round(confidence, 3)))

    def _get_confidence_tier(self, score: float) -> str:
        """Map confidence score to tier."""
        if score >= self.CONFIDENCE_VERY_HIGH:
            return TruthConfidence.VERY_HIGH.value
        elif score >= self.CONFIDENCE_HIGH:
            return TruthConfidence.HIGH.value
        elif score >= self.CONFIDENCE_MEDIUM:
            return TruthConfidence.MEDIUM.value
        elif score >= self.CONFIDENCE_LOW:
            return TruthConfidence.LOW.value
        else:
            return TruthConfidence.VERY_LOW.value

    def _build_truth_signals(
        self,
        sources: List[Dict[str, Any]],
        source_scores: List[float],
        truth_level: int,
        conflict_detected: bool,
        conflict_types: List[str],
        corroborating: int,
        conflicting: int,
        registry_id: Optional[str]
    ) -> Dict[str, Any]:
        """Build the truth signals dictionary."""
        return {
            "truth_level_name": self._get_truth_level_name(truth_level),
            "source_count": len(sources),
            "unique_sources": len(set(s.get('source_id') or s.get('source_hash') for s in sources if s.get('source_id') or s.get('source_hash'))),
            "reliability_scores": {
                s.get('source_id') or s.get('source_hash', 'unknown'): score
                for s, score in zip(sources, source_scores)
            },
            "avg_reliability": round(sum(source_scores) / len(source_scores), 3) if source_scores else 0.0,
            "conflict": {
                "detected": conflict_detected,
                "types": conflict_types,
                "corroborating_sources": corroborating,
                "conflicting_sources": conflicting
            },
            "registry_id": registry_id
        }

    def _get_truth_level_name(self, level: int) -> str:
        """Map truth level to name."""
        names = {
            TruthLevel.UNVERIFIED: "UNVERIFIED",
            TruthLevel.SINGLE_SOURCE: "SINGLE_SOURCE",
            TruthLevel.CORROBORATED: "CORROBORATED",
            TruthLevel.INSTITUTIONAL: "INSTITUTIONAL",
            TruthLevel.PRIMARY_EVIDENCE: "PRIMARY_EVIDENCE"
        }
        return names.get(level, "UNKNOWN")


def resolve_truth_state(
    sources: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    registry_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to resolve truth state.

    Args:
        sources: List of source metadata
        events: List of events
        registry_id: Optional registry reference ID

    Returns:
        Dictionary with truth state output
    """
    engine = TruthStateEngine()
    state = engine.resolve_truth_state(sources, events, registry_id)

    return {
        "truth_level": state.truth_level,
        "truth_level_name": state.truth_signals["truth_level_name"],
        "conflict_flag": state.conflict_flag,
        "confidence_score": state.confidence_score,
        "confidence_tier": state.confidence_tier,
        "corroborating_sources": state.corroborating_sources,
        "conflicting_sources": state.conflicting_sources,
        "source_reliability_avg": state.source_reliability_avg,
        "truth_signals": state.truth_signals
    }
