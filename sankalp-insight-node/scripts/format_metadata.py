import os
import sys
import json
import glob
import datetime as dt
from dateutil import parser as dparser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingest.cleaner import clean_text, detect_language
from agents.summarizer import summarize_short, summarize_medium
from agents.sentiment import analyze

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def today_dir(base):
    d = dt.datetime.utcnow().strftime("%Y%m%d")
    p = os.path.join(base, d)
    ensure_dir(p)
    return p

def pick_category(title):
    t = (title or "").lower()
    if any(x in t for x in ["ai","tech","technology","software","gadgets"]):
        return "technology"
    if any(x in t for x in ["market","stock","economy","business","finance"]):
        return "business"
    if any(x in t for x in ["match","league","tournament","goal","sports"]):
        return "sports"
    if any(x in t for x in ["election","government","policy","politics"]):
        return "politics"
    return "general"

def parse_time(s):
    try:
        return dparser.parse(s).isoformat()
    except Exception:
        return dt.datetime.utcnow().isoformat()

def process_item(it):
    title = clean_text(it.get("title"))
    summary_src = clean_text(it.get("summary"))
    text = (title or "") + ". " + (summary_src or "")
    lang = detect_language(text)
    s_short = summarize_short(text)
    s_med = summarize_medium(text)
    pol, conf, tone = analyze(text)
    cat = pick_category(title)
    ts = parse_time(it.get("published"))
    out = {
        "id": it.get("id") or it.get("link") or os.urandom(8).hex(),
        "title": title,
        "summary_short": s_short,
        "summary_medium": s_med,
        "category": cat,
        "language": lang,
        "polarity": pol,
        "tone": tone,
        "timestamp": ts
    }
    return out

def validate(obj):
    cats = {"general","technology","business","sports","politics"}
    pols = {"positive","neutral","negative"}
    tones = {"calm","urgent","joyful"}
    def ok_str(x, n=1):
        return isinstance(x, str) and len(x.strip()) >= n
    if not ok_str(obj.get("id"), 1):
        return False
    if not ok_str(obj.get("title"), 3):
        return False
    if not ok_str(obj.get("summary_short"), 5):
        return False
    if not ok_str(obj.get("summary_medium"), 5):
        return False
    if obj.get("category") not in cats:
        return False
    if not ok_str(obj.get("language"), 2):
        return False
    if obj.get("polarity") not in pols:
        return False
    if obj.get("tone") not in tones:
        return False
    try:
        _ = dparser.parse(obj.get("timestamp"))
    except Exception:
        return False
    return True

def main():
    raw_dir = today_dir(os.path.join("data","raw"))
    out_dir = today_dir(os.path.join("data","processed"))
    files = sorted(glob.glob(os.path.join(raw_dir, "*.json")))
    items = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fd:
                data = json.load(fd)
        except Exception:
            continue
        for x in (data.get("items", []) or []):
            items.append(x)
    count = 0
    for i, it in enumerate(items):
        obj = process_item(it)
        if validate(obj):
            path = os.path.join(out_dir, f"item_{i+1}.json")
            try:
                with open(path, "w", encoding="utf-8") as fo:
                    json.dump(obj, fo, ensure_ascii=False, indent=2)
                count += 1
            except Exception:
                continue
        if count >= 10:
            break
    print(json.dumps({"processed": count, "output_dir": out_dir}))

if __name__ == "__main__":
    main()