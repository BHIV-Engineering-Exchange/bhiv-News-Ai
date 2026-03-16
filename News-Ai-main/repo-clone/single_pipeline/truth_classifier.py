"""
Truth Classifier Module
Deterministic classification of ingestion events into truth levels 0-4.
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
    Classifies the truth level based on deterministic signals from source metadata.
    
    Order of operations (highest level first):
    1. Direct Documented Evidence (Level 4): source['primary_evidence'] == True or source['document_hash']
    2. Institutional/Primary Source (Level 3): source['is_institutional'] == True or source['authority_score'] >= 0.8
    3. Multi-source Corroborated (Level 2): >= 2 unique source hashes/IDs
    4. Single-source Reported (Level 1): exactly 1 unique source hash/ID
    5. Unverified Claim (Level 0): default if no valid signals
    """
    if not sources:
        return TruthLevel.UNVERIFIED

    # 1. Check for Primary Evidence (Level 4)
    if any(s.get('primary_evidence') is True or s.get('document_hash') for s in sources):
        return TruthLevel.PRIMARY_EVIDENCE

    # 2. Check for Institutional Source (Level 3)
    if any(s.get('is_institutional') is True or s.get('authority_score', 0) >= 0.8 for s in sources):
        return TruthLevel.INSTITUTIONAL

    # Identify unique sources based on source_hash or source_id
    unique_sources = set()
    for s in sources:
        sid = s.get('source_hash') or s.get('source_id')
        if sid:
            unique_sources.add(sid)

    # 3. Check for Multi-source Corroboration (Level 2)
    if len(unique_sources) >= 2:
        return TruthLevel.CORROBORATED

    # 4. Check for Single-source Reported (Level 1)
    if len(unique_sources) == 1:
        return TruthLevel.SINGLE_SOURCE

    # 5. Default: Unverified (Level 0)
    return TruthLevel.UNVERIFIED
