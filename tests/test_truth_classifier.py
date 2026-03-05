from truth_classifier import classify


def test_fabricated():
    a = {"headline": "This is a hoax", "text": "made up story"}
    out = classify(a)
    assert out["truth_level"] == 0


def test_trusted_source():
    a = {"headline": "Official", "source": "reliable.org", "confidence": 0.5}
    out = classify(a)
    assert out["truth_level"] == 4


def test_hedging():
    a = {"headline": "Report reportedly finds", "text": "alleged incident"}
    out = classify(a)
    assert out["truth_level"] == 2


def test_default_plausible():
    a = {"headline": "Community event", "text": "Town hall at 7"}
    out = classify(a)
    assert out["truth_level"] == 3
