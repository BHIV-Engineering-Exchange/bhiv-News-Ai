import copy
import sys
import os

# Ensure repository root is on sys.path so the local package is importable during tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sankalp_insight_node.classification.truth_classifier import classify_with_meta
from sankalp_insight_node.conflict.conflict_detector import detect_conflicts


def test_deterministic_classification():
    source = "https://example.com/news/1"
    content = "Official statement: the ministry announced new guidelines."
    a = classify_with_meta(source, content)
    b = classify_with_meta(source, content)
    assert a["event_id"] == b["event_id"]
    assert a["truth_level"] == b["truth_level"]


def test_conflict_detection():
    source = "https://example.com/news/2"
    content1 = "Reported: a local event occurred, according to sources."
    content2 = "Rumor: a local event occurred, hearsay online."
    r1 = classify_with_meta(source, content1)
    r2 = classify_with_meta("https://other.example/news/2", content2)
    # include content so conflict detector can detect content mismatch
    r1["content"] = content1
    r2["content"] = content2
    records = [r1, r2]
    conflicts = detect_conflicts(records)
    assert isinstance(conflicts, list)
