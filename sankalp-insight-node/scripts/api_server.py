import os
import sys
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.rl_feedback import compute_reward, log_event
from agents.automator import decide, requeue_item

class ApiHandler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return self._send(400, {"error": "invalid_json"})

        if self.path == "/feedback":
            item = payload.get("item", {})
            item_id = payload.get("id") or item.get("id")
            signals = payload.get("signals", {})
            reward = compute_reward(signals)
            action = decide(item, reward)
            log_event({"type": "feedback", "id": item_id, "signals": signals, "reward": reward, "action": action})
            if action == "requeue" and item_id:
                requeued = requeue_item(item_id)
            else:
                requeued = False
            return self._send(200, {"id": item_id, "reward": reward, "action": action, "requeued": requeued})

        if self.path == "/requeue":
            item_id = payload.get("id")
            ok = bool(item_id) and requeue_item(item_id)
            log_event({"type": "requeue", "id": item_id, "ok": ok})
            return self._send(200, {"id": item_id, "requeued": ok})

        return self._send(404, {"error": "not_found"})

def main():
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = int(os.environ.get("API_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), ApiHandler)
    print(f"API server running at http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()