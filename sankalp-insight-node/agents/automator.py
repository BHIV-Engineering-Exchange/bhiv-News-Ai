import os
import glob
import json
import datetime as dt

def thresholds():
    pr = float(os.environ.get("AUTOMATOR_PRIORITY_THRESHOLD", "0.5"))
    rw = float(os.environ.get("AUTOMATOR_REWARD_THRESHOLD", "0.2"))
    esc_pr = float(os.environ.get("AUTOMATOR_ESC_PRIORITY", "0.1"))
    esc_rw = float(os.environ.get("AUTOMATOR_ESC_REWARD", "0.0"))
    return pr, rw, esc_pr, esc_rw

def decide(item, reward):
    pr, rw, esc_pr, esc_rw = thresholds()
    p = float(item.get("priority_score", 0.0))
    if p <= esc_pr and reward <= esc_rw:
        return "escalate"
    if p < pr or reward < rw:
        return "requeue"
    return "none"

def _today_dir(base):
    d = dt.datetime.utcnow().strftime("%Y%m%d")
    p = os.path.join(base, d)
    os.makedirs(p, exist_ok=True)
    return p

def _find_processed_by_id(item_id):
    pdir = _today_dir(os.path.join("data","processed"))
    for f in glob.glob(os.path.join(pdir, "item_*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fd:
                obj = json.load(fd)
            if obj.get("id") == item_id:
                return f, obj
        except Exception:
            continue
    return None, None

def requeue_item(item_id):
    path, obj = _find_processed_by_id(item_id)
    if not path or not obj:
        return False
    obj["requeue_requested"] = True
    try:
        with open(path, "w", encoding="utf-8") as fo:
            json.dump(obj, fo, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False