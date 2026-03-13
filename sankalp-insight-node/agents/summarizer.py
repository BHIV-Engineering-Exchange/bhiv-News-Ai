import os
import re
import requests

def _sentences(text):
    t = text or ""
    s = re.split(r"(?<=[\.!?])\s+", t)
    return [x.strip() for x in s if x.strip()]

def _fallback_short(text):
    s = _sentences(text)
    return " ".join(s[:2])[:400]

def _fallback_medium(text):
    s = _sentences(text)
    return " ".join(s[:4])[:800]

def _uniguru(text):
    url = os.environ.get("https://complete-uniguru.onrender.com")
    key = os.environ.get("uniguru-dev-key-2025")
    if not url:
        return None
    try:
        to = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "20"))
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        payload = {"text": text}
        r = requests.post(url, json=payload, headers=headers, timeout=to)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def summarize_short(text):
    res = _uniguru(text)
    if isinstance(res, dict) and res.get("summary_short"):
        return res.get("summary_short")
    return _fallback_short(text)

def summarize_medium(text):
    res = _uniguru(text)
    if isinstance(res, dict) and res.get("summary_medium"):
        return res.get("summary_medium")
    return _fallback_medium(text)