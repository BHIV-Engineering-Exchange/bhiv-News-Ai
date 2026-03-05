# DEMO Recovery Guide

If the demo experiences failures, follow these step-by-step recovery actions. This guide assumes limited developer access and is written for demo operators.

1) If backend stops responding
   - Check process manager on the demo host (Windows: Task Manager / Services; Linux: systemd `sudo systemctl status newsai`).
   - Restart the service: `sudo systemctl restart newsai` or use the startup script (ask devs for exact command).
   - If the API is still unreachable, check port (default 8000) and firewall rules.
   - Run `python monitor_backend.py --iterations 1` locally to confirm reachability and create an immediate report.

2) If frontend fails or shows UI errors
   - Reload the frontend in the browser (hard refresh: Ctrl+Shift+R).
   - Check browser console for error messages and copy them into the incident note.
   - If UI shows network 5xx/4xx, run `python demo_check.py` to determine if backend endpoints are failing.

3) If pipeline processing stalls
   - Confirm pipeline endpoint via `demo_check.py` to see if pipeline/processing/output endpoints respond.
   - If the pipeline service is down, restart the worker services (ask devs for the worker command).

4) Logs and diagnostics
   - Check `newsai_error_log.json` for recent errors and timestamps.
   - Check `monitor_report.json` for summary statistics and recent latencies.
   - Collect server logs and include last 20 lines in incident report.

5) Safe demo fallback
   - If backend cannot be restored within 5 minutes, switch to pre-recorded demo mode (if available) or notify the audience.
   - Inform stakeholders and resume live demo only after services are healthy.

6) Contact chain
   - Noopur (Backend)
   - Seeya (Orchestration)
   - Chandragupta (Frontend)
   - Vinayak (External tester)

Keep this document handy during the demo and update it with any site-specific commands.
