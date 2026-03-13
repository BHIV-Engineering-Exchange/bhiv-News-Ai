import time
import feedparser

def fetch_rss(url, limit=20):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.get("entries", [])[:limit]:
        items.append({
            "id": entry.get("id") or entry.get("link") or str(time.time()),
            "title": entry.get("title"),
            "link": entry.get("link"),
            "summary": entry.get("summary"),
            "published": entry.get("published"),
            "source": feed.get("feed", {}).get("title") or url
        })
    return items