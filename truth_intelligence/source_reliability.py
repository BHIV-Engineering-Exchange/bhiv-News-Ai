"""
Source Reliability System - Phase 2 of Truth Intelligence Layer.
Scores sources based on institutional credibility, historical accuracy,
repetition frequency, and verification history.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from collections import defaultdict

# Default institutional credibility scores
DEFAULT_INSTITUTIONAL_CREDIBILITY: Dict[str, float] = {
    "reuters": 0.95,
    "associated_press": 0.95,
    "ap": 0.95,
    "bbc": 0.93,
    "pib": 0.95,  # Press Information Bureau (India)
    "pib.gov": 0.95,
    "gov.in": 0.90,
    "gov": 0.88,
    "who": 0.95,
    "un": 0.92,
    "unicef": 0.92,
    "imf": 0.92,
    "world_bank": 0.90,
    "ndma": 0.92,  # National Disaster Management Authority (India)
    "isdm": 0.90,
    "cag": 0.92,   # Comptroller and Auditor General
    "Election_Commission": 0.95,
    "supreme_court": 0.95,
    "high_court": 0.90,
    "parliament": 0.92,
    "loksabha": 0.90,
    "rajyasabha": 0.90,
    "mint": 0.88,
    "the_hindu": 0.85,
    "indian_express": 0.85,
    "toi": 0.82,   # Times of India
    "ht": 0.82,    # Hindustan Times
    "ie": 0.85,    # Indian Express
    "ndtv": 0.80,
    "cnn": 0.85,
    "cnbc": 0.85,
    "bloomberg": 0.88,
    "economist": 0.90,
}

# Source type weights for reliability scoring
SOURCE_TYPE_WEIGHTS = {
    "official": 1.0,
    "news_agency": 0.95,
    "newspaper": 0.85,
    "broadcast": 0.85,
    "digital": 0.80,
    "blog": 0.50,
    "social": 0.30,
    "unknown": 0.40,
}

# Reputation decay factor per false report
REPUTATION_DECAY_PER_FALSE = 0.05
# Minimum reputation score
MIN_REPUTATION_SCORE = 0.10


@dataclass
class SourceReliabilityRecord:
    """Record tracking source reliability metrics."""
    source_id: str
    total_reports: int = 0
    verified_reports: int = 0
    false_reports: int = 0
    institutional_credibility: float = 0.5
    last_verification_score: float = 0.5


class SourceReliabilityScorer:
    """
    Scores sources based on multiple signals:
    - Institutional credibility (domain-based)
    - Historical accuracy (track verified vs false reports)
    - Repetition frequency (how often source is cited)
    - Verification history (past performance)
    """

    def __init__(self):
        self._source_records: Dict[str, SourceReliabilityRecord] = {}
        self._citation_counts: Dict[str, int] = defaultdict(int)

    def get_source_reliability_score(
        self,
        source: Dict[str, Any],
        source_id: Optional[str] = None
    ) -> float:
        """
        Calculate reliability score for a source.

        Score is computed as weighted combination of:
        - Institutional credibility (0-1)
        - Historical accuracy (0-1)
        - Verification reputation (0-1)

        Args:
            source: Source metadata dictionary
            source_id: Optional explicit source identifier

        Returns:
            Reliability score between 0.0 and 1.0
        """
        sid = source_id or source.get('source_id') or source.get('source_hash', 'unknown')

        # Initialize record if not exists
        if sid not in self._source_records:
            self._source_records[sid] = SourceReliabilityRecord(
                source_id=sid,
                institutional_credibility=self._get_institutional_credibility(source)
            )

        record = self._source_records[sid]

        # 1. Institutional credibility (40% weight)
        institutional_score = record.institutional_credibility

        # 2. Historical accuracy (35% weight)
        historical_score = self._calculate_historical_accuracy(record)

        # 3. Verification reputation (25% weight)
        verification_score = record.last_verification_score

        # Weighted combination
        reliability_score = (
            institutional_score * 0.40 +
            historical_score * 0.35 +
            verification_score * 0.25
        )

        # Update citation count
        self._citation_counts[sid] += 1

        return round(reliability_score, 3)

    def _get_institutional_credibility(self, source: Dict[str, Any]) -> float:
        """
        Get institutional credibility based on source domain/identity.
        Returns score between 0.0 and 1.0.
        """
        # Check for explicit authority_score
        if 'authority_score' in source:
            return source['authority_score']

        # Check for institutional flag
        if source.get('is_institutional'):
            return 0.90

        # Check known domains
        source_domain = self._extract_domain(source)
        if source_domain:
            for known_domain, score in DEFAULT_INSTITUTIONAL_CREDIBILITY.items():
                if known_domain in source_domain.lower():
                    return score

        # Check source type
        source_type = source.get('source_type', 'unknown').lower()
        return SOURCE_TYPE_WEIGHTS.get(source_type, 0.50)

    def _extract_domain(self, source: Dict[str, Any]) -> Optional[str]:
        """Extract domain from source URL or name."""
        url = source.get('url') or source.get('source_url') or source.get('domain', '')
        if '://' in url:
            return url.split('://')[1].split('/')[0]
        return url

    def _calculate_historical_accuracy(self, record: SourceReliabilityRecord) -> float:
        """
        Calculate historical accuracy based on verified vs false reports.
        """
        if record.total_reports == 0:
            return 0.50  # Neutral - no history

        # Accuracy ratio
        accuracy_ratio = record.verified_reports / record.total_reports

        # Decay for false reports
        false_decay = record.false_reports * REPUTATION_DECAY_PER_FALSE

        # Final score with decay applied
        score = max(accuracy_ratio - false_decay, MIN_REPUTATION_SCORE)
        return min(score, 1.0)

    def update_source_verification(
        self,
        source_id: str,
        verified: bool,
        total_reports: Optional[int] = None,
        verified_reports: Optional[int] = None,
        false_reports: Optional[int] = None
    ) -> None:
        """
        Update source verification history.

        Args:
            source_id: Source identifier
            verified: Whether the report was verified as true
            total_reports: Optional explicit total count
            verified_reports: Optional explicit verified count
            false_reports: Optional explicit false count
        """
        if source_id not in self._source_records:
            self._source_records[source_id] = SourceReliabilityRecord(source_id=source_id)

        record = self._source_records[source_id]

        if total_reports is not None:
            record.total_reports = total_reports
        else:
            record.total_reports += 1

        if verified_reports is not None:
            record.verified_reports = verified_reports
        elif verified:
            record.verified_reports += 1

        if false_reports is not None:
            record.false_reports = false_reports
        elif not verified:
            record.false_reports += 1

        # Recalculate verification score
        record.last_verification_score = self._calculate_historical_accuracy(record)

    def get_source_citation_count(self, source_id: str) -> int:
        """Get how many times a source has been cited."""
        return self._citation_counts.get(source_id, 0)

    def get_source_record(self, source_id: str) -> Optional[SourceReliabilityRecord]:
        """Get the reliability record for a source."""
        return self._source_records.get(source_id)


# Global scorer instance for consistent scoring across pipeline
_global_scorer = SourceReliabilityScorer()


def get_source_reliability_score(source: Dict[str, Any], source_id: Optional[str] = None) -> float:
    """
    Get reliability score for a source using global scorer.

    Args:
        source: Source metadata dictionary
        source_id: Optional explicit source identifier

    Returns:
        Reliability score between 0.0 and 1.0
    """
    return _global_scorer.get_source_reliability_score(source, source_id)


def update_source_verification(source_id: str, verified: bool) -> None:
    """
    Update verification history for a source.

    Args:
        source_id: Source identifier
        verified: Whether the report was verified as true
    """
    _global_scorer.update_source_verification(source_id, verified)


def get_source_metadata(source: Dict[str, Any], source_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get complete source reliability metadata.

    Args:
        source: Source metadata dictionary
        source_id: Optional explicit source identifier

    Returns:
        Dictionary with reliability metadata
    """
    sid = source_id or source.get('source_id') or source.get('source_hash', 'unknown')
    score = get_source_reliability_score(source, sid)
    citations = _global_scorer.get_source_citation_count(sid)
    record = _global_scorer.get_source_record(sid)

    return {
        "source_id": sid,
        "reliability_score": score,
        "citation_count": citations,
        "is_reliable": score >= 0.70,
        "reliability_tier": _get_reliability_tier(score),
        "total_reports": record.total_reports if record else 0,
        "verified_reports": record.verified_reports if record else 0,
        "false_reports": record.false_reports if record else 0
    }


def _get_reliability_tier(score: float) -> str:
    """Map score to reliability tier."""
    if score >= 0.90:
        return "VERY_HIGH"
    elif score >= 0.80:
        return "HIGH"
    elif score >= 0.70:
        return "MEDIUM"
    elif score >= 0.50:
        return "LOW"
    else:
        return "VERY_LOW"
