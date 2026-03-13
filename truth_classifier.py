"""
Truth Classifier Module
Deterministic classification of truth signals into levels 0-4.
"""

from typing import List, Dict, Any, Optional

class TruthLevel:
    UNVERIFIED = 0          # Unverified claim
    SINGLE_SOURCE = 1      # Single-source report
    CORROBORATED = 2        # Multi-source corroboration
    AUTHORITATIVE = 3      # Institutional / primary authority source
    PRIMARY_EVIDENCE = 4   # Direct documented or primary evidence

def classify_truth_level(sources: List[Dict[str, Any]]) -> int:
    """
    Classifies truth level based on source metadata.
    Deterministic and rule-based.
    """
    if not sources:
        return TruthLevel.UNVERIFIED

    # Check for primary evidence (Level 4)
    # Primary evidence is defined as a source with 'primary_evidence' = True
    # or a direct link to a document/official transcript.
    if any(s.get('primary_evidence', False) for s in sources):
        return TruthLevel.PRIMARY_EVIDENCE

    # Check for authoritative/institutional sources (Level 3)
    # Authoritative sources have 'authority_level' >= 3
    if any(s.get('authority_level', 0) >= 3 for s in sources):
        return TruthLevel.AUTHORITATIVE

    # Check for multi-source corroboration (Level 2)
    # Multi-source is defined as >= 2 distinct source identifiers.
    unique_sources = {s.get('source_id') for s in sources if s.get('source_id')}
    if len(unique_sources) >= 2:
        return TruthLevel.CORROBORATED

    # Check for single-source (Level 1)
    if len(unique_sources) == 1:
        return TruthLevel.SINGLE_SOURCE

    # Default to unverified
    return TruthLevel.UNVERIFIED
