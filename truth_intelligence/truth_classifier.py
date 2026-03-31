"""
Truth Classifier Module - Phase 1 of Truth Intelligence Layer.
Deterministic classification of truth signals into levels 0-4.
"""

from typing import List, Dict, Any, Optional

class TruthLevel:
    """Truth classification levels."""
    UNVERIFIED = 0          # Unverified claim - no valid sources
    SINGLE_SOURCE = 1       # Single-source report
    CORROBORATED = 2        # Multi-source corroboration (>=2 sources)
    INSTITUTIONAL = 3       # Institutional / primary authority source
    PRIMARY_EVIDENCE = 4    # Direct documented or primary evidence
    # Backwards-compatible alias used in some tests
    AUTHORITATIVE = INSTITUTIONAL

# Priority order for classification (highest first)
_TRUTH_PRIORITY = [
    TruthLevel.PRIMARY_EVIDENCE,
    TruthLevel.INSTITUTIONAL,
    TruthLevel.CORROBORATED,
    TruthLevel.SINGLE_SOURCE,
    TruthLevel.UNVERIFIED,
]

def classify_truth_level(sources: List[Dict[str, Any]]) -> int:
    """
    Classifies truth level based on source metadata.
    Deterministic and rule-based.

    Classification Priority (highest wins):
    1. PRIMARY_EVIDENCE (4): Any source has primary_evidence=True or document_hash
    2. INSTITUTIONAL (3): Any source has is_institutional=True or authority_score>=0.8
    3. CORROBORATED (2): >=2 unique source_ids present
    4. SINGLE_SOURCE (1): Exactly 1 unique source_id present
    5. UNVERIFIED (0): Default - no sources or no identifiable source

    Args:
        sources: List of source metadata dictionaries

    Returns:
        Truth level (0-4)
    """
    if not sources:
        return TruthLevel.UNVERIFIED

    # Level 4: Primary evidence
    # Direct documented evidence - document_hash or primary_evidence flag
    if any(_has_primary_evidence(s) for s in sources):
        return TruthLevel.PRIMARY_EVIDENCE

    # Level 3: Institutional authority
    # is_institutional flag or high authority_score
    if any(_is_institutional(s) for s in sources):
        return TruthLevel.INSTITUTIONAL

    # Level 2: Multi-source corroboration
    unique_sources = _get_unique_source_ids(sources)
    if len(unique_sources) >= 2:
        return TruthLevel.CORROBORATED

    # Level 1: Single source
    if len(unique_sources) == 1:
        return TruthLevel.SINGLE_SOURCE

    # Level 0: Unverified
    return TruthLevel.UNVERIFIED


def _has_primary_evidence(source: Dict[str, Any]) -> bool:
    """Check if source contains primary evidence signals."""
    if source.get('primary_evidence') is True:
        return True
    if source.get('document_hash'):
        return True
    return False


def _is_institutional(source: Dict[str, Any]) -> bool:
    """Check if source is institutional/authoritative."""
    if source.get('is_institutional') is True:
        return True
    # Accept both floating authority_score (0.0-1.0) and integer authority_level (1-5)
    if source.get('authority_score', 0) >= 0.8:
        return True
    if source.get('authority_level') is not None:
        try:
            if float(source.get('authority_level')) >= 3:
                return True
        except (ValueError, TypeError):
            pass
    return False


def _get_unique_source_ids(sources: List[Dict[str, Any]]) -> set:
    """Extract unique source identifiers from sources."""
    source_ids = set()
    for s in sources:
        sid = s.get('source_id') or s.get('source_hash')
        if sid:
            source_ids.add(sid)
    return source_ids


def get_event_truth_metadata(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Wraps truth classifier output for event ingestion.

    Args:
        sources: List of source metadata

    Returns:
        Dictionary with truth_level
    """
    return {
        "truth_level": classify_truth_level(sources),
        "truth_level_name": _get_truth_level_name(classify_truth_level(sources)),
        "source_count": len(sources),
        "unique_source_count": len(_get_unique_source_ids(sources))
    }


def _get_truth_level_name(level: int) -> str:
    """Map truth level to human-readable name."""
    names = {
        TruthLevel.UNVERIFIED: "UNVERIFIED",
        TruthLevel.SINGLE_SOURCE: "SINGLE_SOURCE",
        TruthLevel.CORROBORATED: "CORROBORATED",
        TruthLevel.INSTITUTIONAL: "INSTITUTIONAL",
        TruthLevel.PRIMARY_EVIDENCE: "PRIMARY_EVIDENCE"
    }
    return names.get(level, "UNKNOWN")
