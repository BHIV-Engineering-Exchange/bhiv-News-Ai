#!/usr/bin/env python3
"""
Lightweight persistent monitoring script for News AI backend.

Designed to run as a background process (daemon) or a scheduled task.
Checks endpoints every 30 seconds and logs failures to structured files.

Usage:
  python monitor_backend.py --daemon  # Runs in persistent 30s loop
  python monitor_backend.py --check-once # Runs a single check and exits
"""
import argparse
import json
import time
from datetime import datetime
from statistics import mean
import os
import sys
import logging

# Configure standard logging for the monitor itself
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("monitor_service.log"),
        logging.StreamHandler()
    ]
)

try:
    import requests
except Exception:
    logging.error("Missing dependency 'requests'. Install with: pip install requests")
    sys.exit(1)

ERROR_LOG = "newsai_error_log.json"
REPORT = "monitor_report.json"
CONFIG_FILE = "monitor_config.json"

# Default endpoints (overridden by monitor_config.json when present)
DEFAULT_ENDPOINTS = {
    "backend_root": os.getenv("MONITOR_BACKEND_ROOT", "http://localhost:8000/"),
    "api_health": os.getenv("MONITOR_API_HEALTH", "http://localhost:8000/health"),
    "pipeline": os.getenv("MONITOR_PIPELINE", "http://localhost:8000/api/unified-news-workflow"),
    "processing": os.getenv("MONITOR_PROCESSING", "http://localhost:8000/api/fast-news-workflow"),
    "output": os.getenv("MONITOR_OUTPUT", "http://localhost:8000/exports/weekly_report.json"),
}

# Default alerting config
DEFAULT_ALERTING = {
    "slack_webhook": None,
    "smtp": None,
    "notify_on_failures": 1,
}


def append_error(entry):
    """
    Appends an error entry to newsai_error_log.json automatically.
    This function is exposed so other components can log here.
    """
    if not os.path.exists(ERROR_LOG):
        with open(ERROR_LOG, "w", encoding="utf-8") as f:
            json.dump([], f)
    try:
        with open(ERROR_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []
    
    # Ensure entry has required fields
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    data.append(entry)
    
    # Keep log file manageable (last 500 entries)
    if len(data) > 500:
        data = data[-500:]
        
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
        error_msg = str(e)
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": error_msg,
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
            "error": error_msg,
        }


def monitor(endpoints, interval=30, iterations=None):
    summary = {k: {"latencies": [], "checks": 0, "failures": 0} for k in endpoints}
    start_time = datetime.utcnow().isoformat() + "Z"
    loop = 0
    alerted = {k: False for k in endpoints}
    
    logging.info(f"Monitor started at {start_time}")
    
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
                    logging.warning(f"FAILURE detected on {name}: {res.get('status') or 'TIMEOUT/ERROR'}")
                    
                    # Log detailed error entry
                    entry = {
                        "timestamp": res.get("timestamp"),
                        "error": res.get("error") if "error" in res else f"HTTP {res.get('status')}",
                        "endpoint": name,
                        "url": url,
                        "status": res.get("status"),
                    }
                    append_error(entry)
                    
                    # Slack alerting
                    try:
                        cfg = load_config()
                        alert_cfg = cfg.get("alerting", DEFAULT_ALERTING)
                    except Exception:
                        alert_cfg = DEFAULT_ALERTING
                        
                    if alert_cfg.get("slack_webhook") and not alerted.get(name):
                        send_slack_alert(alert_cfg["slack_webhook"], name, url, entry["error"]) 
                        alerted[name] = True
                else:
                    if alerted.get(name):
                        logging.info(f"RECOVERY detected on {name}")
                        try:
                            cfg = load_config()
                            alert_cfg = cfg.get("alerting", DEFAULT_ALERTING)
                        except Exception:
                            alert_cfg = DEFAULT_ALERTING
                        if alert_cfg.get("slack_webhook"):
                            send_slack_recovery(alert_cfg["slack_webhook"], name, url)
                        alerted[name] = False
            
            # Update report after each loop
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
                logging.info(f"Completed {iterations} iterations. Exiting.")
                return report
                
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Monitor stopped by user.")
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=30, help="Seconds between checks (default 30)")
    p.add_argument("--iterations", type=int, default=None, help="Number of iterations to run")
    p.add_argument("--endpoints-file", type=str, default=None, help="JSON file with endpoints mapping")
    p.add_argument("--check-once", action="store_true", help="Run one check and exit")
    p.add_argument("--daemon", action="store_true", help="Run in persistent 30s loop (default)")
    args = p.parse_args()

    if args.check_once:
        args.iterations = 1

    # Load config
    endpoints = DEFAULT_ENDPOINTS.copy()
    try:
        config = load_config()
        endpoints = config.get("endpoints", endpoints)
    except Exception:
        pass
        
    if args.endpoints_file:
        try:
            with open(args.endpoints_file, "r", encoding="utf-8") as f:
                endpoints = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load endpoints file: {e}")
            sys.exit(1)

    logging.info(f"Monitoring {len(endpoints)} endpoints every {args.interval}s.")
    monitor(endpoints, interval=args.interval, iterations=args.iterations)


def load_config(path=CONFIG_FILE):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def send_slack_alert(webhook, endpoint, url, error):
    if not webhook:
        return
    payload = {"text": f"[NewsAI Monitor] ALERT: {endpoint} failed at {datetime.utcnow().isoformat()}Z - {error}\n{url}"}
    try:
        requests.post(webhook, json=payload, timeout=5)
    except Exception:
        pass


def send_slack_recovery(webhook, endpoint, url):
    if not webhook:
        return
    payload = {"text": f"[NewsAI Monitor] RECOVERY: {endpoint} recovered at {datetime.utcnow().isoformat()}Z - {url}"}
    try:
        requests.post(webhook, json=payload, timeout=5)
    except Exception:
        pass


if __name__ == "__main__":
    main()
