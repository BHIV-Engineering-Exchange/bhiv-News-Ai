"""
Conflict detection module.

API:
 - detect_conflicts(events: List[dict]) -> Dict[str, bool]

Behavior:
 - Groups events by 'registry_reference_id' (if missing, treated as unique id per event)
 - For each group, compares events pairwise for structural contradictions:
   - Conflicting numeric values for same key
   - Opposing categorical/string values for same key
   - Incompatible explicit states under 'state' or 'status' keys
 - Returns mapping registry_reference_id -> conflict_flag (True/False)

Deterministic and rule-based. Does not merge or resolve entries.
"""
from typing import List, Dict, Any


def _is_number(val: Any) -> bool:
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def _compare_two(e1: Dict[str, Any], e2: Dict[str, Any]) -> bool:
    # Returns True if a structural contradiction exists between e1 and e2
    keys = set(e1.keys()) & set(e2.keys())
    # Exclude metadata-like keys
    exclude = {"updated_at", "created_at", "id", "event_id", "source_id"}
    keys = keys - exclude

    for k in keys:
        v1 = e1.get(k)
        v2 = e2.get(k)
        if v1 is None or v2 is None:
            continue
        # numeric contradiction
        if _is_number(v1) and _is_number(v2):
            if v1 != v2:
                return True
        else:
            # categorical/string contradiction (different non-empty strings)
            if isinstance(v1, str) and isinstance(v2, str) and v1.strip() and v2.strip():
                if v1 != v2:
                    return True
            # Different booleans
            if isinstance(v1, bool) and isinstance(v2, bool) and v1 != v2:
                return True

    # Special check for states/status keys that are typically mutually exclusive
    for s_key in ("state", "status", "event_state"):
        if s_key in e1 and s_key in e2:
            if isinstance(e1[s_key], str) and isinstance(e2[s_key], str) and e1[s_key] != e2[s_key]:
                return True

    return False


def detect_conflicts(events: List[Dict[str, Any]]) -> Dict[str, bool]:
    """Return conflict flags grouped by registry_reference_id.

    For events without a `registry_reference_id`, a unique synthetic id is used
    so they are treated independently (no cross-event conflict unless the id matches).
    """
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for i, ev in enumerate(events):
        rid = ev.get("registry_reference_id")
        if rid is None:
            # synthetic id to avoid grouping unrelated events
            rid = f"__local__{i}"
        groups.setdefault(str(rid), []).append(ev)

    result: Dict[str, bool] = {}
    for rid, group in groups.items():
        conflict = False
        n = len(group)
        # pairwise comparisons
        for i in range(n):
            for j in range(i + 1, n):
                if _compare_two(group[i], group[j]):
                    conflict = True
                    break
            if conflict:
                break
        result[rid] = conflict

    return result


if __name__ == "__main__":
    # quick smoke test
    evs = [
        {"registry_reference_id": "r1", "value": 10, "status": "open"},
        {"registry_reference_id": "r1", "value": 11, "status": "open"},
    ]
    print(detect_conflicts(evs))
