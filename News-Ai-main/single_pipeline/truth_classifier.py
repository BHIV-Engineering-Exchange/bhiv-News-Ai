"""
Deterministic Truth Classification Engine for Samachar.
Assigns truth_level based on rule-based signals only.
"""

from typing import List, Dict, Any

def classify_truth(sources: List[Dict[str, Any]]) -> int:
    """
    Classifies the truth level of an ingestion event based on source signals.
    
    Levels:
    0 — Unverified claim: No valid sources or signals.
    1 — Single-source reported: Exactly one valid source.
    2 — Multi-source corroborated: Two or more unique source hashes/IDs.
    3 — Institutional or primary source: Source marked as institutional (e.g., official gov, verified news agency).
    4 — Direct documented evidence: Source includes a primary document hash or direct evidence flag.
    
    Rules are deterministic and follow a priority order (highest level first).
    """
    if not sources:
        return 0
    
    # Check for Level 4: Direct documented evidence
    if any(source.get('primary_evidence') is True or source.get('document_hash') for source in sources):
        return 4
        
    # Check for Level 3: Institutional or primary source
    if any(source.get('is_institutional') is True or source.get('authority_score', 0) >= 0.8 for source in sources):
        return 3
        
    # Count unique source hashes to distinguish Level 1 and 2
    unique_source_hashes = {source.get('source_hash') for source in sources if source.get('source_hash')}
    
    if len(unique_source_hashes) >= 2:
        return 2
    elif len(unique_source_hashes) == 1:
        return 1
        
    return 0
