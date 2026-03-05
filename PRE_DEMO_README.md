# Pre-Demo Quick Start

Use this guide to run essential checks and produce monitoring artifacts before a live demo.

1) Run the monitor once and generate a clean JSON report

```powershell
cd "Task2-master"
python monitor_backend.py --backend-url http://localhost:8000 --iterations 1 --report > monitor_report.json
```

2) Generate the HTML dashboard

```powershell
python generate_dashboard.py
# opens monitor_dashboard.html in the workspace root
```

3) Run the demo safety checker (quick gate)

```powershell
python demo_check.py --backend-url http://localhost:8000 --out demo_check_report.json
cat demo_check_report.json
```

4) Run the pre-demo wrapper

```powershell
python pre_demo_check.py http://localhost:8000
```

5) Watch for alerts

- To run the alert watcher once:

```powershell
python alert_watch.py
```

- To schedule on Windows (Task Scheduler): create a task that runs every minute with the above command.

6) If issues found

- Follow `DEMO_RECOVERY.md` for restart and recovery steps.
