#!/usr/bin/env python3
"""Simple alert watcher for `newsai_error_log.json`.

This script can be run periodically (or by scheduler) to check the
error log for recent CRITICAL-like entries and print a short alert or
write to `latest_alert.txt`.
"""
import json
import os
from datetime import datetime, timedelta

LOG_FILE = "newsai_error_log.json"
ALERT_OUT = "latest_alert.txt"


def check_alerts(since_minutes=10):
    if not os.path.exists(LOG_FILE):
        return None
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            return None

    cutoff = datetime.now() - timedelta(minutes=since_minutes)
    recent = [e for e in data if datetime.fromisoformat(e.get("timestamp")) >= cutoff]
    if not recent:
        return None

    # Build simple summary
    summary = {"checked_at": datetime.now().isoformat(), "count": len(recent), "samples": recent[-5:]}
    return summary


def main():
    s = check_alerts()
    if s:
        with open(ALERT_OUT, "w", encoding="utf-8") as f:
            f.write(json.dumps(s, indent=2))
        print(f"ALERT: {s['count']} recent errors. Wrote {ALERT_OUT}")
    else:
        print("No recent alerts.")


if __name__ == "__main__":
    main()
