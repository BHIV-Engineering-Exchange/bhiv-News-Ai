#!/usr/bin/env python3
"""Simple conflict detector for two article-like items.

Provides lightweight, deterministic heuristics to flag obvious contradictions
between two observations without modifying any pipeline logic. This is a
starter module for testing and documentation.
"""
from typing import Dict, Any, Tuple, List
import re


def _extract_numbers(text: str):
    return [float(x.replace(',', '')) for x in re.findall(r"\d+[\d,\.]*", text)]


def _normalize(text: str) -> str:
    return (text or "").lower()


def detect_conflict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Return dict {conflict: bool, reasons: [str]}.

    Heuristics:
    - Negation conflicts: "not X" vs "X"
    - Numerical contradictions: differing numbers present in both
    - Direct opposite verbs (simple list) or explicit denial vs confirmation
    """
    reasons: List[str] = []
    headline_a = _normalize(a.get("headline") or a.get("title") or "")
    headline_b = _normalize(b.get("headline") or b.get("title") or "")
    text_a = _normalize(a.get("text") or "")
    text_b = _normalize(b.get("text") or "")

    joined_a = f"{headline_a} {text_a}".strip()
    joined_b = f"{headline_b} {text_b}".strip()

    # Negation heuristic
    for word in [" not ", "n't ", " no "]:
        # look for pattern 'not X' in one and 'X' in the other
        if word in joined_a:
            # take token after 'not '
            m = re.search(r"not\s+(\w+)", joined_a)
            if m and m.group(1) and m.group(1) in joined_b:
                reasons.append(f"Negation: '{m.group(0)}' vs affirmative in other")
        if word in joined_b:
            m = re.search(r"not\s+(\w+)", joined_b)
            if m and m.group(1) and m.group(1) in joined_a:
                reasons.append(f"Negation: '{m.group(0)}' vs affirmative in other")

    # Numeric contradictions
    nums_a = _extract_numbers(joined_a)
    nums_b = _extract_numbers(joined_b)
    if nums_a and nums_b:
        # compare first found numbers
        if abs(nums_a[0] - nums_b[0]) > 0.1 * max(abs(nums_a[0]), abs(nums_b[0]), 1):
            reasons.append(f"Numeric mismatch: {nums_a[0]} vs {nums_b[0]}")

    # Denial vs confirmation simple keywords
    denies = ["deny", "denies", "refute", "refutes", "reject"]
    confirms = ["confirm", "confirms", "confirmed", "admits", "acknowledge"]
    if any(w in joined_a for w in denies) and any(w in joined_b for w in confirms):
        reasons.append("One item denies while the other confirms")
    if any(w in joined_b for w in denies) and any(w in joined_a for w in confirms):
        reasons.append("One item denies while the other confirms")

    conflict = len(reasons) > 0
    return {"conflict": conflict, "reasons": reasons}


if __name__ == "__main__":
    a = {"headline": "X not guilty, says source", "text": "No charges"}
    b = {"headline": "X found guilty by court", "text": "Court confirms conviction"}
    print(detect_conflict(a, b))
