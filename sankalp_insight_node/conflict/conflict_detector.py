from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List


def detect_conflicts(records: Iterable[Dict]) -> List[Dict]:
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
