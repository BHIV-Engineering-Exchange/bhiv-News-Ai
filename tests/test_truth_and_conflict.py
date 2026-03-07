import copy
from truth_classifier import classify_claim
from conflict_detector import detect_conflicts


def test_classify_levels():
    # level 4 (direct)
    e = {"sources": [], "evidence": [{"evidence_type": "direct"}]}
    assert classify_claim(e) == 4

    # level 3 (institutional)
    e = {"sources": [], "evidence": [{"evidence_type": "institutional"}]}
    assert classify_claim(e) == 3

    # level 2 (multi-source)
    e = {"sources": ["a", "b"], "evidence": []}
    assert classify_claim(e) == 2

    # level 2 (two reports)
    e = {"sources": [], "evidence": [{"evidence_type": "report"}, {"evidence_type": "report"}]}
    assert classify_claim(e) == 2

    # level 1 (single source)
    e = {"sources": ["only"], "evidence": []}
    assert classify_claim(e) == 1

    # level 0 (none)
    e = {"sources": [], "evidence": []}
    assert classify_claim(e) == 0


def test_deterministic_classification():
    base = {"sources": ["s1"], "evidence": [{"evidence_type": "report"}]}
    a = classify_claim(base)
    b = classify_claim(copy.deepcopy(base))
    assert a == b


def test_conflict_detection_numeric():
    evs = [
        {"registry_reference_id": "r1", "value": 10},
        {"registry_reference_id": "r1", "value": 11},
    ]
    res = detect_conflicts(evs)
    assert res.get("r1") is True


def test_conflict_detection_no_conflict():
    evs = [
        {"registry_reference_id": "r2", "value": 10},
        {"registry_reference_id": "r2", "value": 10},
    ]
    res = detect_conflicts(evs)
    assert res.get("r2") is False


def test_conflict_detection_categorical():
    evs = [
        {"registry_reference_id": "r3", "status": "open"},
        {"registry_reference_id": "r3", "status": "closed"},
    ]
    res = detect_conflicts(evs)
    assert res.get("r3") is True
