#!/usr/bin/env python3
"""Generate a simple HTML dashboard from `monitor_report.json`.

Writes `monitor_dashboard.html` into the same directory.
"""
import json
import os
from datetime import datetime


def build_html(report: dict) -> str:
    title = f"Monitor Report - {report.get('report_generated', '')}"
    lines = ["<html><head><meta charset='utf-8'><title>", title, "</title></head><body>"]
    lines.append(f"<h1>{title}</h1>")
    lines.append(f"<p>Backend: {report.get('backend_url')}</p>")
    lines.append(f"<p>Total checks: {report.get('total_checks')}, Total errors: {report.get('total_errors')}</p>")

    lines.append("<h2>Recent status</h2>")
    for check in report.get('recent_checks', []):
        lines.append(f"<div style='border:1px solid #ccc;padding:8px;margin:8px;'>")
        lines.append(f"<strong>{check.get('timestamp')}</strong> - {check.get('status')}")
        lines.append("<ul>")
        for c in check.get('critical_checks', []) + check.get('operational_checks', []):
            color = 'green' if c.get('healthy') else 'red'
            lines.append(f"<li><span style='color:{color}'>[{c.get('method')}] {c.get('endpoint')} - {c.get('latency_ms')}ms</span></li>")
        lines.append("</ul>")
        lines.append("</div>")

    lines.append("<footer><small>Generated at " + datetime.now().isoformat() + "</small></footer>")
    lines.append("</body></html>")
    return "\n".join(lines)


def main():
    path = os.path.join(os.path.dirname(__file__), 'monitor_report.json')
    if not os.path.exists(path):
        print('monitor_report.json not found')
        return
    with open(path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    html = build_html(report)
    out = os.path.join(os.path.dirname(__file__), 'monitor_dashboard.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Wrote: {out}')


if __name__ == '__main__':
    main()
