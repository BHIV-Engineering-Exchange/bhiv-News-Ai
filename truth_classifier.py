#!/usr/bin/env python3
"""Deterministic truth classifier (starter)

This module provides a small, fully deterministic classifier that maps
article-like dictionaries to a `truth_level` integer (0-4) with a
rationale string. It is intentionally simple and isolated so it can be
used as a transparent reference implementation and unit-tested without
touching the production pipeline.

Rules (deterministic):
- 0 (Fabricated): explicit tokens like 'fabricat', 'hoax', 'false'
- 1 (Satire): tokens like 'satire', 'parody'
- 4 (Verified): trusted source OR confidence >= 0.90
- 2 (Needs verification): tokens like 'alleged', 'reportedly', 'claims'
- 3 (Plausible/Unverified): default fallback

The classifier does not call external services and uses only string
heuristics and numeric thresholds so its outputs are repeatable.
"""
from typing import Dict, Any, Tuple
import re

TRUSTED_SOURCES = {"trustednews.com", "reliable.org", "official.gov"}


def _find_token(text: str, tokens):
    if not text:
        return False
    text_l = text.lower()
    for t in tokens:
        if t in text_l:
            return True
    return False


def classify(article: Dict[str, Any]) -> Dict[str, Any]:
    """Classify an `article` dict and return `{'truth_level': int, 'rationale': str}`.

    Expected keys (not required): `headline`, `text`, `source`, `confidence`.
    """
    headline = (article.get("headline") or "")
    text = (article.get("text") or "")
    source = (article.get("source") or "").lower()
    confidence = article.get("confidence")

    # Tokens
    fabricated_tokens = ["fabricat", "hoax", "false", "made up"]
    satire_tokens = ["satire", "parody", "spoof"]
    verify_tokens = ["alleged", "reportedly", "claims", "according to"]

    joined = " ".join([headline, text])

    # Rule: Fabricated
    if _find_token(joined, fabricated_tokens):
        return {"truth_level": 0, "rationale": "Detected fabricated/hoax tokens"}

    # Rule: Satire
    if _find_token(joined, satire_tokens):
        return {"truth_level": 1, "rationale": "Detected satire/parody tokens"}

    # Rule: Verified by trusted source or very high confidence
    if source and any(s in source for s in TRUSTED_SOURCES):
        return {"truth_level": 4, "rationale": f"Source in trusted list: {source}"}

    try:
        if confidence is not None:
            conf = float(confidence)
            if conf >= 0.90:
                return {"truth_level": 4, "rationale": f"High confidence: {conf}"}
    except Exception:
        pass

    # Rule: Needs verification
    if _find_token(joined, verify_tokens):
        return {"truth_level": 2, "rationale": "Contains hedging/attribution language"}

    # Default: plausible but unverified
    return {"truth_level": 3, "rationale": "Default plausible/unverified"}


def classify_batch(articles):
    return [classify(a) for a in articles]


if __name__ == "__main__":
    # Quick self-check
    samples = [
        {"headline": "This is a hoax story", "text": "Completely fabricated", "source": "unknown"},
        {"headline": "Official release from reliable.org", "source": "reliable.org", "confidence": 0.95},
        {"headline": "Local report reportedly says...", "text": "alleged theft reported"},
    ]
    for s in samples:
        print(s, "->", classify(s))
