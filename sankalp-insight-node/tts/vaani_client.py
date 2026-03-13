import os
import base64
import requests

def synthesize(text, voice="default", tone="calm", lang="en", out_path=None):
    base = os.environ.get("VAANI_TTS_URL")
    key = os.environ.get("VAANI_API_KEY")
    if not base:
        return None
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    payload = {"text": text, "voice": voice, "tone": tone, "lang": lang}
    urls = [base]
    if base.rstrip("/").endswith("/api/v1"):
        urls = [base.rstrip("/") + "/tts", base]
    to = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "20"))
    for url in urls:
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=to)
            if r.status_code >= 400:
                continue
            ct = r.headers.get("Content-Type", "")
            if "audio" in ct:
                if not out_path:
                    return r.content
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return out_path
            data = r.json()
            if isinstance(data, dict):
                if data.get("audio_base64"):
                    b = base64.b64decode(data.get("audio_base64"))
                    if out_path:
                        with open(out_path, "wb") as f:
                            f.write(b)
                        return out_path
                    return b
                if data.get("audio_url"):
                    ar = requests.get(data.get("audio_url"), timeout=to)
                    if ar.status_code >= 400:
                        continue
                    if out_path:
                        with open(out_path, "wb") as f:
                            f.write(ar.content)
                        return out_path
                    return ar.content
        except Exception:
            continue
    return None