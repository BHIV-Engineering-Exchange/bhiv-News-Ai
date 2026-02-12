import os
import json
import datetime as dt

DEFAULT_WEIGHTS = {
    "editor_approve": 1.0,
    "user_like": 0.6,
    "user_skip": -0.4,
    "manual_override": -0.8
}

def get_weights():
    w = dict(DEFAULT_WEIGHTS)
    raw = os.environ.get("RL_WEIGHTS_JSON")
    if raw:
        try:
            ext = json.loads(raw)
            w.update({k: float(v) for k, v in ext.items() if k in w})
        except Exception:
            pass
    return w

def compute_reward(signals, weights=None):
    w = weights or get_weights()
    s = dict(signals or {})
    r = 0.0
    for k, val in s.items():
        if k in w:
            r += (w[k] * (1 if bool(val) else 0))
    return round(max(-1.0, min(1.0, r)), 4)

def log_event(event):
    path = os.path.join("logs", "rl_events.log")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            rec = dict(event or {})
            rec["ts"] = dt.datetime.utcnow().isoformat()
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass