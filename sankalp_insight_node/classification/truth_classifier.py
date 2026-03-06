"""Deterministic truth classifier (duplicate for importable package).

This file mirrors sankalp-insight-node/classification/truth_classifier.py
but lives under a Python-importable package name (underscore) so tests can
import `sankalp_insight_node.classification`.
"""
from __future__ import annotations

import hashlib
from typing import Dict


def _event_id(source: str, content: str) -> str:
    key = f"{source}|{content}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()


def _rule_based_truth_level(content: str) -> (int, str):
    lc = content.lower()
    if any(k in lc for k in ("official", "announced", "confirmed", "statement")):
        return 4, "official/confirmed wording"
    if any(k in lc for k in ("reported", "sources say", "according to")):
        return 3, "reported / sourced"
    if any(k in lc for k in ("unverified", "alleged", "may have")):
        return 2, "unverified/alleged"
    if any(k in lc for k in ("rumor", "rumours", "hearsay")):
        return 1, "rumor/hearsay"
    if any(k in lc for k in ("satire", "not true", "fake news", "hoax")):
        return 0, "satire/explicitly false"
    words = lc.split()
    if len(words) < 6:
        return 1, "short text heuristic -> low confidence"
    return 2, "default fallback -> medium confidence"


def classify_with_meta(source: str, content: str) -> Dict[str, object]:
    eid = _event_id(source, content)
    level, reason = _rule_based_truth_level(content)
    return {"event_id": eid, "truth_level": level, "reason": reason, "source": source}


def classify(source: str, content: str) -> int:
    return classify_with_meta(source, content)["truth_level"]
