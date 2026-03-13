import os
import requests

def fetch_newsdata(query, language="en", page_size=10):
    key = os.environ.get("NEWSDATA_API_KEY")
    if not key:
        return []
    url = "https://newsdata.io/api/1/news"
    params = {"apikey": key, "q": query, "language": language, "page": 1}
    results = []
    to = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "20"))
    r = requests.get(url, params=params, timeout=to)
    r.raise_for_status()
    data = r.json()
    for item in data.get("results", [])[:page_size]:
        results.append(item)
    return results