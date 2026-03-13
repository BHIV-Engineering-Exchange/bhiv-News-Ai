import os
import sys
import json
import datetime as dt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingest.rss_reader import fetch_rss

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def out_dir():
    date_str = dt.datetime.utcnow().strftime("%Y%m%d")
    p = os.path.join("data", "raw", date_str)
    ensure_dir(p)
    return p

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def main():
    sources = [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.npr.org/1004/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://www.theverge.com/rss/index.xml"
    ]
    outp = out_dir()
    for i, url in enumerate(sources):
        items = fetch_rss(url, limit=20)
        path = os.path.join(outp, f"rss_{i+1}.json")
        write_json(path, {"source_url": url, "count": len(items), "items": items})

if __name__ == "__main__":
    main()