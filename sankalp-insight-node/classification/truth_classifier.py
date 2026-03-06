"""Deterministic truth classifier for Samachar alignment.

This module provides a small, deterministic rule-based classifier that
assigns a `truth_level` in the range 0..4 and produces a stable `event_id`
derived from `source` and `content` using SHA256. The rules are intentionally
simple and documented in ../docs/truth_classification_rules.md so they are
transparent and reproducible.
"""
from __future__ import annotations

import hashlib
from typing import Dict


def _event_id(source: str, content: str) -> str:
    """Return a deterministic hex event id for the given source+content."""
    key = f"{source}|{content}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()


def _rule_based_truth_level(content: str) -> (int, str):
    """Deterministically choose a truth level (0..4) and reason string.

    Rules are simple keyword-based checks ordered from strongest indicators
    of veracity to weakest. They are deterministic and do not use randomness.
    """
    lc = content.lower()
    # Strong signals for highly trustworthy (4)
    if any(k in lc for k in ("official", "announced", "confirmed", "statement")):
        return 4, "official/confirmed wording"
    # Signals for likely verified/reporting (3)
    if any(k in lc for k in ("reported", "sources say", "according to")):
        return 3, "reported / sourced"
    # Ambiguous/unverified mentions (2)
    if any(k in lc for k in ("unverified", "alleged", "may have")):
        return 2, "unverified/alleged"
    # Rumor-like signals (1)
    if any(k in lc for k in ("rumor", "rumours", "hearsay")):
        return 1, "rumor/hearsay"
    # Satire or explicit false claims (0)
    if any(k in lc for k in ("satire", "not true", "fake news", "hoax")):
        return 0, "satire/explicitly false"
    # Fallback deterministic heuristic: length+word cues
    words = lc.split()
    if len(words) < 6:
        return 1, "short text heuristic -> low confidence"
    return 2, "default fallback -> medium confidence"


def classify_with_meta(source: str, content: str) -> Dict[str, object]:
    """Classify content and return a deterministic metadata dictionary.

    Returns dict with keys: `event_id`, `truth_level`, `reason`, `source`.
    """
    eid = _event_id(source, content)
    level, reason = _rule_based_truth_level(content)
    return {"event_id": eid, "truth_level": level, "reason": reason, "source": source}


def classify(source: str, content: str) -> int:
    """Shortcut to return only the `truth_level` integer."""
    return classify_with_meta(source, content)["truth_level"]


if __name__ == "__main__":
    # small demo when run directly
    sample = classify_with_meta("example.com/article/1", "Official statement: company announced acquisition.")
    print(sample)
