#!/usr/bin/env python3
"""Generate a clean monitoring report (JSON) without console output."""
import os
import json
from monitor_backend import NewsAIMonitor

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def main():
    monitor = NewsAIMonitor(backend_url=BACKEND_URL, monitor_interval=30)
    # Perform a single health check
    monitor.run_health_check()
    report = monitor.generate_report()
    out_path = os.path.join(os.path.dirname(__file__), "monitor_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote: {out_path}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Generate monitor report - standalone script."""

import sys
import os
import json

# Ensure proper encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import after encoding config
from monitor_backend import NewsAIMonitor

def generate_report():
    """Generate health report."""
    monitor = NewsAIMonitor(backend_url='http://localhost:8000')
    check_result = monitor.run_health_check()
    report = monitor.generate_report()
    return report

if __name__ == "__main__":
    try:
        report = generate_report()
        with open('monitor_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=True)
        print("Report generated: monitor_report.json")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
