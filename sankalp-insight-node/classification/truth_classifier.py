"""
Deterministic Truth Classification Engine for Samachar.
Assigns truth_level based on rule-based signals only.
"""

from typing import List, Dict, Any, Optional

class TruthLevel:
    UNVERIFIED = 0          # Unverified claim
    SINGLE_SOURCE = 1      # Single-source reported
    CORROBORATED = 2        # Multi-source corroborated
    INSTITUTIONAL = 3      # Institutional or primary source
    PRIMARY_EVIDENCE = 4   # Direct documented evidence

def classify_truth_level(sources: List[Dict[str, Any]]) -> int:
    """
    Classifies the truth level of an ingestion event based on source signals.
    
    Deterministic priority (highest match wins):
    4. Direct Documented Evidence: If any source contains a valid document_hash or primary_evidence flag.
    3. Institutional / Primary: If any source is flagged as is_institutional or has authority_score >= 0.8.
    2. Multi-Source: If 2 or more unique source_hashes are present.
    1. Single-Source: If exactly 1 unique source_hash is present.
    0. Unverified: Default case.
    
    If uncertain, the lower level is assigned.
    """
    if not sources:
        return TruthLevel.UNVERIFIED

    # Identify unique sources based on source_hash
    unique_source_hashes = {str(s.get('source_hash')).strip() for s in sources if s.get('source_hash')}
    num_unique = len(unique_source_hashes)

    # Level 4: Direct documented evidence
    # Look for 'document_hash' or explicit 'primary_evidence' signal
    if any(s.get('primary_evidence') is True or s.get('document_hash') for s in sources):
        return TruthLevel.PRIMARY_EVIDENCE

    # Level 3: Institutional or primary authority
    # Look for 'is_institutional' flag or high 'authority_score'
    for s in sources:
        try:
            score = float(s.get('authority_score', 0))
        except (ValueError, TypeError):
            score = 0.0
        if s.get('is_institutional') is True or score >= 0.8:
            return TruthLevel.INSTITUTIONAL

    # Level 2: Multi-source corroboration
    if num_unique >= 2:
        return TruthLevel.CORROBORATED

    # Level 1: Single-source reported
    if num_unique == 1:
        return TruthLevel.SINGLE_SOURCE

    # Default Level 0: Unverified claim
    return TruthLevel.UNVERIFIED

def get_event_truth_metadata(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Wraps the classifier output for Samachar event ingestion.
    """
    return {
        "truth_level": classify_truth_level(sources)
    }
