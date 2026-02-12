import math

POS = {"good","great","positive","benefit","growth","optimistic","gain","win","strong","record","surge","rise","improve","success","joy","happy"}
NEG = {"bad","poor","negative","loss","drop","decline","fall","weak","crisis","fear","warn","risk","fail","collapse","urgent","emergency"}
URGENT = {"breaking","urgent","emergency","crisis","alert","deadline"}

def _score(text):
    t = (text or "").lower()
    p = sum(1 for w in POS if w in t)
    n = sum(1 for w in NEG if w in t)
    s = p - n
    if s > 0:
        pol = "positive"
    elif s < 0:
        pol = "negative"
    else:
        pol = "neutral"
    conf = min(1.0, (p+n)/5.0) if (p+n)>0 else 0.3
    if any(w in t for w in URGENT):
        tone = "urgent"
    elif p > n and p > 0:
        tone = "joyful"
    else:
        tone = "calm"
    return pol, float(f"{conf:.2f}"), tone

def analyze(text):
    return _score(text)