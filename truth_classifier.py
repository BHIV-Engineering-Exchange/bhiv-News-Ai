"""
Deterministic truth classifier (truth_level 0-4).

API:
 - classify_claim(event: dict) -> int

Expected input event fields (no schema mutation; function reads these keys if present):
 - "sources": list of source identifiers (can be empty)
 - "evidence": list of dicts with key "evidence_type" values in {"direct","institutional","report"}

Rules (deterministic, explicit):
 - 4: any evidence item with evidence_type == "direct"
 - 3: any evidence item with evidence_type == "institutional"
 - 2: if distinct sources count >= 2 OR at least two corroborating evidence items (report)
 - 1: if exactly one source and no higher rule matched
 - 0: otherwise (unverified)

No randomness, no probabilistic inference, no schema changes.
"""
from typing import Dict, List, Any

def _count_distinct_sources(event: Dict[str, Any]) -> int:
    sources = event.get("sources") or []
    try:
        return len(set(sources))
    except TypeError:
        # non-hashable sources -> fallback to length
        return len(list(sources))

def _evidence_types(event: Dict[str, Any]) -> List[str]:
    ev = event.get("evidence") or []
    types = []
    for item in ev:
        if not isinstance(item, dict):
            continue
        t = item.get("evidence_type")
        if isinstance(t, str):
            types.append(t.lower())
    return types

def classify_claim(event: Dict[str, Any]) -> int:
    """Deterministically classify an event into truth_level 0-4.

    The function is pure: same input dict (content-wise) always returns the
    same integer. It avoids heuristics beyond simple counts and explicit tags.
    """
    # Rule 4: direct documented / primary evidence
    types = _evidence_types(event)
    if "direct" in types:
        return 4

    # Rule 3: institutional / primary authority source
    if "institutional" in types:
        return 3

    # Rule 2: multi-source corroboration
    distinct_sources = _count_distinct_sources(event)
    if distinct_sources >= 2:
        return 2

    # Also treat multiple 'report' evidence items as corroboration
    if types.count("report") >= 2:
        return 2

    # Rule 1: single-source report
    if distinct_sources == 1 or types.count("report") == 1:
        return 1

    # Rule 0: unverified claim
    return 0


if __name__ == "__main__":
    # quick smoke check
    sample = {"sources": ["s1"], "evidence": [{"evidence_type": "report"}]}
    print(classify_claim(sample))
