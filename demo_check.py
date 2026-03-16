#!/usr/bin/env python3
"""
🚀 News AI Demo Safety Checker

Performs a rigorous check of all critical production endpoints.
Outputs a clear SAFE or UNSAFE status for demo operators.
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
REPORT_FILE = "demo_check_report.json"

DEFAULTS = {
    "pipeline": os.getenv("MONITOR_PIPELINE", "http://localhost:8000/api/unified-news-workflow"),
    "processing": os.getenv("MONITOR_PROCESSING", "http://localhost:8000/api/fast-news-workflow"),
    "output": os.getenv("MONITOR_OUTPUT", "http://localhost:8000/exports/weekly_report.json"),
}

def log_event(entry):
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

    print("\n" + "="*50)
    print("🔍 NEWS AI - PRE-DEMO SAFETY CHECK")
    print("="*50)

    checks = [
        ("Pipeline Status", args.pipeline),
        ("Processing API", args.processing),
        ("Output Delivery", args.output)
    ]
    
    failures = []
    details = []
    
    for name, url in checks:
        print(f"Checking {name:20} ... ", end="", flush=True)
        status, latency, err = check(url)
        
        d = {"endpoint": name, "url": url, "status": status, "latency_s": latency, "error": err}
        details.append(d)
        
        if err or status is None or status >= 400:
            print("❌ FAILED")
            failures.append(f"{name}: {err or f'HTTP {status}'}")
        elif latency > args.latency_threshold:
            print("⚠️ SLOW")
            failures.append(f"{name}: High Latency ({latency:.2f}s)")
        else:
            print(f"✅ OK ({latency:.2f}s)")

    print("-" * 50)
    
    if not failures:
        print("\n🏆 RESULT: SAFE")
        print("System is healthy and ready for live demonstration.")
        status_code = 0
    else:
        print("\n🚨 RESULT: UNSAFE")
        print("Detected issues that may disrupt the demo:")
        for f in failures:
            print(f"  - {f}")
        print("\n👉 ACTION: Consult DEMO_RECOVERY.md immediately.")
        status_code = 2

    # Log results to centralized error log if unsafe
    if failures:
        log_event({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "DEMO_SAFETY_CHECK_FAILURE",
            "failures": failures
        })

    # Write detailed report
    report = {
        "checked_at": datetime.utcnow().isoformat() + "Z",
        "result": "SAFE" if not failures else "UNSAFE",
        "failures": failures,
        "details": details
    }
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print("="*50 + "\n")
    sys.exit(status_code)

if __name__ == "__main__":
    main()
