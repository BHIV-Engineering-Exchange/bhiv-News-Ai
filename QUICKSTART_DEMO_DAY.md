# Demo Day Quick Start
## News AI – Get Live in 5 Minutes

**Your job**: Run these commands in order. The system will tell you if something's wrong.

---

## Step 1: Terminal 1 – Start Backend

```powershell
cd "c:\Users\user11\Desktop\News AI\Task2-master\unified_tools_backend"
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Wait** until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Step 2: Terminal 2 – Safety Check

```powershell
cd "c:\Users\user11\Desktop\News AI\Task2-master"
python demo_check.py
```

**You should see**:
```
[OK] Demo Status: SAFE | Passed: 4/5 | Failed Critical: 0
✓ DEMO IS READY TO PROCEED
```

**If you see** `[FAIL]` instead of `[OK]` → Open `DEMO_RECOVERY.md` and look for that error.

---

## Step 3: Terminal 3 – Start Monitoring

```powershell
cd "c:\Users\user11\Desktop\News AI\Task2-master"
python monitor_backend.py
```

Keep this running. You'll see updates every 30 seconds. If you see `[FAIL]`, something broke.

---

## Step 4: (Optional) Terminal 4 – Start Frontend

```powershell
cd "c:\Users\user11\Desktop\News AI\Task2-master\blackhole-frontend"
npm run dev
```

Navigate to `http://localhost:3000` in browser.

---

## During Demo

✓ System is live and monitoring  
✓ All terminals keep running  
✓ If something fails:
  1. Check Terminal 3 (monitoring)
  2. Open `newsai_error_log.json` (last error)
  3. See `DEMO_RECOVERY.md` for what to do

---

## Quick Fixes (If Something's Wrong)

| Problem | Command |
|---------|---------|
| "Cannot connect" | Check Terminal 1 - is backend running? |
| "Not authenticated" | Backend is running but needs auth token (normal for demo) |
| Slow response (>2sec) | Check server load; might clear up by itself |
| Nothing's working | Run this: `Ctrl+C` in all terminals, then restart Step 1 |

---

## File Reference

- `demo_check.py` – Safety gate before demo
- `monitor_backend.py` – Live monitoring (keep running)
- `newsai_error_log.json` – Error history
- `DEMO_RECOVERY.md` – Full troubleshooting guide (read if stuck)

---

**That's it. You're live.** Good luck with the demo! 🚀
