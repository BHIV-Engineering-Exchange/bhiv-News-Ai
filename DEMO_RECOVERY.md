# 🛠️ NEWS AI - Demo Recovery Guide (Operator Edition)

This guide provides **immediate, step-by-step recovery actions** for demo operators. If the system fails during a live demonstration, follow these steps in order.

---

## 🛑 Step 0: The "Quick Fix"
1.  **Hard Refresh**: Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac) in the browser.
2.  **Check Status**: Run the safety checker to identify the root cause:
    ```bash
    python demo_check.py
    ```
    - If it says **SAFE**, the issue is likely your browser or internet connection.
    - If it says **UNSAFE**, follow the specific scenario below.

---

## 📉 Scenario A: Backend Stopped Responding
*Symptoms: UI shows "Connection Refused" or "Backend Offline".*

1.  **Kill Existing Processes**:
    - **Windows**: Open Task Manager, find all `python.exe` or `uvicorn` processes and "End Task".
    - **Linux/Mac**: Run `pkill -f uvicorn`.
2.  **Restart Backend**:
    ```bash
    cd unified_tools_backend
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
3.  **Verify**: Visit `http://localhost:8000/health` in your browser. It should show `{"status": "healthy"}`.

---

## 🔄 Scenario B: Pipeline is Stalled
*Symptoms: Analysis gets stuck at 0% or a specific stage for >60 seconds.*

1.  **Restart Worker**:
    If the system uses a background worker (e.g., Celery or a separate thread), restart it:
    ```bash
    python queue_worker.py  # (Verify if this is the correct command for your environment)
    ```
2.  **Clear Local Cache**:
    If specific URLs fail, try a different news URL (e.g., from BBC or Reuters) to rule out scraping issues.

---

## 🌐 Scenario C: Frontend UI Glitches
*Symptoms: Layout is broken, buttons don't click.*

1.  **Restart Frontend**:
    ```bash
    cd blackhole-frontend
    npm run dev -- -p 3002
    ```
2.  **Check Port**: Ensure the frontend is running on port **3002** as expected by the demo setup.

---

## 📊 Diagnostic Logs
If the above steps fail, check these files for the last 5 lines:
- **Error Details**: `newsai_error_log.json`
- **Uptime Stats**: `monitor_report.json`
- **Monitor Service**: `monitor_service.log`

---

## 📞 Emergency Contacts
| Role | Name | Channel |
| :--- | :--- | :--- |
| **Backend** | Noopur | Slack / Internal |
| **Frontend** | Chandragupta | Slack / Internal |
| **Demo Lead** | Sankalp | Slack / Internal |
| **Tester** | Vinayak | Slack / Internal |

---
*Last Updated: 2026-03-13*
