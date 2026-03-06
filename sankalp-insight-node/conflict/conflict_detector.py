"""Simple conflict detection utilities for Samachar alignment.

This module provides deterministic rules to detect conflicting records for the
same `event_id` (different `truth_level`) or same `event_id` with differing
`content` coming from distinct sources.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List


def detect_conflicts(records: Iterable[Dict]) -> List[Dict]:
    """Detect conflicts in a list of records.

    Each record is expected to contain at least: `event_id`, `truth_level`,
    `content`, and `source`.

    Returns a list of conflict descriptions.
    """
    by_event = defaultdict(list)
    for r in records:
        by_event[r["event_id"]].append(r)

    conflicts = []
    for event_id, items in by_event.items():
        levels = {i.get("truth_level") for i in items}
        contents = {i.get("content") for i in items}
        sources = {i.get("source") for i in items}
        if len(levels) > 1:
            conflicts.append({"event_id": event_id, "type": "truth_level_mismatch", "levels": list(levels), "count": len(items)})
        if len(contents) > 1 and len(sources) > 1:
            conflicts.append({"event_id": event_id, "type": "content_mismatch", "sources": list(sources), "count": len(items)})
    return conflicts


if __name__ == "__main__":
    demo = [
        {"event_id": "e1", "truth_level": 3, "content": "A", "source": "s1"},
        {"event_id": "e1", "truth_level": 1, "content": "A different", "source": "s2"},
    ]
    print(detect_conflicts(demo))
