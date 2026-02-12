import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    path = os.path.join("exports","weekly_report.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"items": []}
    items = data.get("items", [])[:9]
    out = []
    def normalize_path(p):
        if not p:
            return p
        return str(p).replace("\\", "/")
    for x in items:
        y = {
            "id": x.get("id"),
            "script": x.get("summary_medium") or x.get("summary_short") or x.get("title"),
            "tone": x.get("tone"),
            "language": x.get("language"),
            "audio_path": normalize_path(x.get("audio_path")),
            "priority_score": x.get("priority_score"),
            "trend_score": x.get("trend_score")
        }
        out.append(y)
    outp = os.path.join("exports","sample_integration.json")
    try:
        with open(outp, "w", encoding="utf-8") as fo:
            json.dump({"items": out}, fo, ensure_ascii=False, indent=2)
    except Exception:
        pass
    print(json.dumps({"written": outp, "count": len(out)}))

if __name__ == "__main__":
    main()