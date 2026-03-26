"""
Samachar API - Ingestion layer wrapper.
POST /api/samachar/process
"""

import os
import sys
import json
import datetime as dt
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# Add sankalp-insight-node to path
SANKALP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sankalp-insight-node")
sys.path.insert(0, SANKALP_PATH)

from ingest.cleaner import clean_text, detect_language
from agents.summarizer import summarize_short, summarize_medium
from agents.sentiment import analyze

CATS = {"general", "technology", "business", "sports", "politics"}
POLS = {"positive", "neutral", "negative"}
TONES = {"calm", "urgent", "joyful"}

def pick_category(title):
    t = (title or "").lower()
    if any(x in t for x in ["ai", "tech", "technology", "software", "gadgets"]):
        return "technology"
    if any(x in t for x in ["market", "stock", "economy", "business", "finance"]):
        return "business"
    if any(x in t for x in ["match", "league", "tournament", "goal", "sports"]):
        return "sports"
    if any(x in t for x in ["election", "government", "policy", "politics"]):
        return "politics"
    return "general"

def process_text(raw_text: str) -> dict:
    """
    Core pipeline: raw text -> structured event JSON.
    """
    sentences = [s.strip() for s in (raw_text or "").split(".") if s.strip()]
    title = sentences[0] if sentences else (raw_text or "")[:100]
    summary_src = ". ".join(sentences[:2]) if sentences else raw_text

    text = title + ". " + summary_src
    lang = detect_language(text)
    s_short = summarize_short(text)
    s_med = summarize_medium(text)
    pol, conf, tone = analyze(text)
    cat = pick_category(title)
    ts = dt.datetime.utcnow().isoformat()

    return {
        "id": os.urandom(8).hex(),
        "title": title,
        "summary_short": s_short,
        "summary_medium": s_med,
        "category": cat,
        "language": lang,
        "polarity": pol,
        "tone": tone,
        "timestamp": ts
    }

def validate_output(obj: dict) -> bool:
    """Validate output has required fields and valid values."""
    if not isinstance(obj.get("title"), str) or len(obj["title"].strip()) < 3:
        return False
    if not isinstance(obj.get("summary_short"), str) or len(obj["summary_short"].strip()) < 5:
        return False
    if obj.get("category") not in CATS:
        return False
    if obj.get("polarity") not in POLS:
        return False
    if obj.get("tone") not in TONES:
        return False
    return True

class SamacharHandler(BaseHTTPRequestHandler):
    def _send(self, code: int, obj: dict):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return self._send(400, {"error": "invalid JSON body"})

        if self.path != "/api/samachar/process":
            return self._send(404, {"error": "not found"})

        raw_text = payload.get("text")
        if not raw_text:
            return self._send(400, {"error": "text field is required"})

        if not isinstance(raw_text, str):
            return self._send(400, {"error": "text must be a string"})

        try:
            result = process_text(raw_text)
            if not validate_output(result):
                return self._send(500, {"error": "pipeline produced invalid output"})
            return self._send(200, result)
        except Exception as e:
            return self._send(500, {"error": f"pipeline error: {str(e)}"})

def main():
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), SamacharHandler)
    print(f"Samachar API running at http://{host}:{port}/api/samachar/process")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
