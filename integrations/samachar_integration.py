"""
Samachar integration wrapper (truth emission only).

Constraints:
- Do NOT modify input events or their schema.
- Do NOT add new fields to events.
- Produce separate truth signals (no merging/resolution).
- Deterministic, rule-based, replayable.

API:
- emit_truth_signals(events: List[dict]) -> List[dict]

Each returned signal dict contains:
- registry_reference_id (or synthetic id)
- event_id if present on original event
- truth_level (int 0-4)
- conflict_flag (bool)

This module calls `truth_classifier.classify_claim` and
`conflict_detector.detect_conflicts` without mutating the original events.
"""
from typing import List, Dict, Any
from truth_classifier import classify_claim
from conflict_detector import detect_conflicts


def emit_truth_signals(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate truth signals for a batch of events.

    Does not mutate `events`. Returns a list of signal dicts.
    """
    # compute truth_level per event
    signals: List[Dict[str, Any]] = []
    # copy minimal needed data for conflict detector grouping
    for ev in events:
        # classifier reads only 'sources' and 'evidence' keys
        tl = classify_claim(ev)
        signals.append({
            "registry_reference_id": ev.get("registry_reference_id"),
            "event_id": ev.get("event_id"),
            "truth_level": tl,
            # placeholder for conflict_flag; fill after conflict detection
            "conflict_flag": False,
        })

    # prepare lightweight events for conflict detection (use original events as-is)
    conflicts = detect_conflicts(events)

    # attach conflict flags deterministically (lookup by registry_reference_id)
    for s in signals:
        rid = s.get("registry_reference_id")
        if rid is None:
            # match synthetic ids used in detector (detector uses __local__index for None)
            # replicate behavior: try to find a matching event index
            # (fall back: no conflict)
            s["conflict_flag"] = False
        else:
            s["conflict_flag"] = bool(conflicts.get(str(rid), False))

    return signals


def emit_truth_signal_for_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience wrapper for single event.

    Returns a single signal dict; does not modify the event.
    """
    sigs = emit_truth_signals([event])
    return sigs[0]


if __name__ == "__main__":
    # simple smoke
    ev = {"registry_reference_id": "r1", "sources": ["s1"], "evidence": []}
    print(emit_truth_signal_for_event(ev))
