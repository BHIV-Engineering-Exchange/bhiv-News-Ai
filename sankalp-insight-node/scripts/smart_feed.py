import os
import sys
import glob
import json
import math
import datetime as dt
import argparse
from dateutil import parser as dparser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.trend import compute as compute_trend

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def today_dir(base, date_override=None):
    d = date_override or dt.datetime.utcnow().strftime("%Y%m%d")
    p = os.path.join(base, d)
    ensure_dir(p)
    return p

def _ts(s):
    try:
        t = dparser.parse(s)
        if t.tzinfo is not None:
            t = t.astimezone(dt.timezone.utc).replace(tzinfo=None)
        return t
    except Exception:
        return dt.datetime.utcnow()

def recency_score(ts):
    now = dt.datetime.utcnow()
    dh = max(0.0, (now - _ts(ts)).total_seconds()/3600.0)
    return max(0.0, min(1.0, max(0.0, 1.0 - dh/48.0)))

def normalize_path(p):
    if not p:
        return p
    return str(p).replace("\\", "/")

def polarity_weight(p):
    if p == "positive":
        return 1.0
    if p == "neutral":
        return 0.6
    return 0.4

def priority(item, trend_scores):
    c = item.get("category") or "general"
    trend = float(trend_scores.get(c, 0.0))
    polw = float(polarity_weight(item.get("polarity")))
    conf = float(item.get("confidence", 0.5)) if item.get("confidence") is not None else 0.5
    rec = float(recency_score(item.get("timestamp")))
    score = 0.4*trend + 0.2*polw + 0.2*conf + 0.2*rec
    return round(min(1.0, max(0.0, score)), 4)

def rank(items):
    tscores = compute_trend(items)
    ranked = []
    for x in items:
        s = priority(x, tscores)
        y = dict(x)
        y["trend_score"] = round(tscores.get(x.get("category") or "general", 0.0), 4)
        y["priority_score"] = s
        if y.get("audio_path"):
            y["audio_path"] = normalize_path(y.get("audio_path"))
        ranked.append(y)
    ranked.sort(key=lambda z: z["priority_score"], reverse=True)
    return ranked

def export_weekly(feed):
    out_dir = os.path.join("exports")
    ensure_dir(out_dir)
    csv_path = os.path.join(out_dir, "weekly_report.csv")
    json_path = os.path.join(out_dir, "weekly_report.json")
    try:
        with open(csv_path, "w", encoding="utf-8") as fc:
            fc.write("id,title,category,language,polarity,tone,trend_score,priority_score,timestamp\n")
            for x in feed:
                row = [
                    str(x.get("id","")).replace(","," "),
                    str(x.get("title","")).replace(","," "),
                    x.get("category",""),
                    x.get("language",""),
                    x.get("polarity",""),
                    x.get("tone",""),
                    str(x.get("trend_score","")),
                    str(x.get("priority_score","")),
                    x.get("timestamp","")
                ]
                fc.write(",".join(row)+"\n")
    except Exception:
        pass
    sanitized = []
    for x in feed:
        y = dict(x)
        if y.get("audio_path"):
            y["audio_path"] = normalize_path(y.get("audio_path"))
        sanitized.append(y)
    try:
        with open(json_path, "w", encoding="utf-8") as fj:
            json.dump({"generated_at": dt.datetime.utcnow().isoformat(), "items": sanitized}, fj, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return csv_path, json_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYYMMDD date to read from", default=None)
    args = ap.parse_args()
    pdir = today_dir(os.path.join("data","processed"), args.date)
    files = sorted(glob.glob(os.path.join(pdir, "item_*.json")))
    items = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fd:
                items.append(json.load(fd))
        except Exception:
            continue
    feed = rank(items)
    cats = {}
    for x in feed:
        c = x.get("category") or "general"
        cats.setdefault(c, []).append(x)
    for c, arr in cats.items():
        cats[c] = arr[:10]
    csv_path, json_path = export_weekly(feed)
    print(json.dumps({"categories": list(cats.keys()), "top_counts": {k: len(v) for k,v in cats.items()}, "csv": csv_path, "json": json_path}))

if __name__ == "__main__":
    main()