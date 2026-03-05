#!/usr/bin/env python3
"""
Lightweight monitoring script for News AI backend.

Default behaviour: run checks every 30 seconds (configurable) and log
errors to `newsai_error_log.json`. For simulation/testing you can run
with `--iterations N` and a smaller `--interval`.

This script does NOT modify any backend logic or schemas.
"""
import argparse
import json
import time
from datetime import datetime
from statistics import mean
import os
import sys

try:
    import requests
except Exception:
    print("Missing dependency 'requests'. Install with: pip install requests")
    sys.exit(1)

ERROR_LOG = "newsai_error_log.json"
REPORT = "monitor_report.json"

DEFAULT_ENDPOINTS = {
    "backend_root": "http://localhost:8000/",
    "api_health": "http://localhost:8000/health",
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


def write_report(report):
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)


def check_endpoint(name, url, timeout=5):
    start = time.time()
    try:
        r = requests.get(url, timeout=timeout)
        latency = time.time() - start
        status = r.status_code
        ok = 200 <= status < 400
        return {
            "endpoint": name,
            "url": url,
            "ok": ok,
            "status": status,
            "latency_s": round(latency, 3),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        latency = time.time() - start
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
            "endpoint": name,
            "url": url,
            "status": None,
        }
        append_error(entry)
        return {
            "endpoint": name,
            "url": url,
            "ok": False,
            "status": None,
            "latency_s": round(latency, 3),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
        }


def monitor(endpoints, interval=30, iterations=None):
    summary = {k: {"latencies": [], "checks": 0, "failures": 0} for k in endpoints}
    start_time = datetime.utcnow().isoformat() + "Z"
    loop = 0
    try:
        while True:
            loop += 1
            results = []
            for name, url in endpoints.items():
                res = check_endpoint(name, url)
                results.append(res)
                summary[name]["checks"] += 1
                summary[name]["latencies"].append(res.get("latency_s", 0))
                if not res.get("ok", False):
                    summary[name]["failures"] += 1
                    # Log error entry for status >=400
                    entry = {
                        "timestamp": res.get("timestamp"),
                        "error": res.get("error") if "error" in res else f"HTTP {res.get('status')}",
                        "endpoint": name,
                        "url": url,
                        "status": res.get("status"),
                    }
                    append_error(entry)
            # update report after each loop
            report = {
                "start_time": start_time,
                "last_run": datetime.utcnow().isoformat() + "Z",
                "loop": loop,
                "results": results,
                "summary": {},
            }
            for name, stats in summary.items():
                lat = stats["latencies"]
                report["summary"][name] = {
                    "checks": stats["checks"],
                    "failures": stats["failures"],
                    "avg_latency_s": round(mean(lat), 3) if lat else None,
                    "last_latency_s": round(lat[-1], 3) if lat else None,
                }
            write_report(report)
            if iterations is not None and loop >= iterations:
                return report
            time.sleep(interval)
    except KeyboardInterrupt:
        return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=30, help="Seconds between checks (default 30)")
    p.add_argument("--iterations", type=int, default=None, help="Number of iterations to run (for tests)")
    p.add_argument("--endpoints-file", type=str, default=None, help="JSON file with endpoints mapping")
    args = p.parse_args()

    endpoints = DEFAULT_ENDPOINTS.copy()
    if args.endpoints_file:
        try:
            with open(args.endpoints_file, "r", encoding="utf-8") as f:
                endpoints = json.load(f)
        except Exception as e:
            print("Failed to load endpoints file:", e)
            sys.exit(1)

    print(f"Monitoring {len(endpoints)} endpoints every {args.interval}s. Press Ctrl-C to stop.")
    report = monitor(endpoints, interval=args.interval, iterations=args.iterations)
    print("Final report written to", REPORT)


if __name__ == "__main__":
    main()
