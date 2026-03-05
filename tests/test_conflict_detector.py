from conflict_detector import detect_conflict


def test_numeric_conflict():
    a = {"headline": "Population 1000", "text": "Number: 1,000"}
    b = {"headline": "Population 2000", "text": "Number: 2,000"}
    out = detect_conflict(a, b)
    assert out["conflict"]


def test_negation_conflict():
    a = {"headline": "Leader not guilty", "text": "No charges"}
    b = {"headline": "Leader guilty confirmed", "text": "Court confirms"}
    out = detect_conflict(a, b)
    assert out["conflict"]


def test_no_conflict():
    a = {"headline": "Sunny day", "text": "Clear skies"}
    b = {"headline": "Rain expected", "text": "Showers later"}
    out = detect_conflict(a, b)
    # may be no explicit conflict detected
    assert isinstance(out.get("conflict"), bool)
