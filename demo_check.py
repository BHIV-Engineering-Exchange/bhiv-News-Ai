#!/usr/bin/env python3
"""
Simple demo safety checker. Tests pipeline, processing and output endpoints
and prints SAFE or UNSAFE.
"""
import argparse
import json
import sys
import time
from datetime import datetime
import os

try:
    import requests
except Exception:
    print("Missing dependency 'requests'. Install with: pip install requests")
    sys.exit(1)

ERROR_LOG = "newsai_error_log.json"

DEFAULTS = {
    "pipeline": "http://localhost:8000/pipeline/status",
    "processing": "http://localhost:8000/process",
    "output": "http://localhost:8000/output",
}


def append_error(entry):
    if not os.path.exists(ERROR_LOG):
        with open(ERROR_LOG, "w", encoding="utf-8") as f:
            json.dump([], f)
    try:
        with open(ERROR_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []
    data.append(entry)
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def check(url, timeout=5):
    start = time.time()
    try:
        r = requests.get(url, timeout=timeout)
        latency = time.time() - start
        return r.status_code, latency, None
    except Exception as e:
        return None, None, str(e)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pipeline", default=DEFAULTS["pipeline"])
    p.add_argument("--processing", default=DEFAULTS["processing"])
    p.add_argument("--output", default=DEFAULTS["output"])
    p.add_argument("--latency-threshold", type=float, default=2.0)
    args = p.parse_args()

    checks = [("pipeline", args.pipeline), ("processing", args.processing), ("output", args.output)]
    unsafe = False
    details = []
    for name, url in checks:
        status, latency, err = check(url)
        d = {"endpoint": name, "url": url, "status": status, "latency_s": latency, "error": err}
        details.append(d)
        if err or status is None or status >= 400 or (latency is not None and latency > args.latency_threshold):
            unsafe = True
            entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": err if err else f"HTTP {status}",
                "endpoint": name,
                "url": url,
                "status": status,
            }
            append_error(entry)

    result = "SAFE" if not unsafe else "UNSAFE"
    print(result)
    # write a small local report for quick inspection
    report = {"checked_at": datetime.utcnow().isoformat() + "Z", "result": result, "details": details}
    with open("demo_check_report.json", "w", encoding="utf-8") as f:
        import json

        json.dump(report, f, indent=2, default=str)

    sys.exit(0 if result == "SAFE" else 2)


if __name__ == "__main__":
    main()
