# Demo Recovery Guide – News AI

## Quick Reference

**Before Demo**: Run `python demo_check.py`  
**During Demo**: Keep `monitor_backend.py` running in background  
**If Demo Fails**: Use the recovery steps below

---

## Status Indicators

| Status | Meaning | Action |
|--------|---------|--------|
| ✓ SAFE | Demo ready | Proceed safely |
| ⚠ DEGRADED | Some issues, may still work | Monitor closely |
| ✗ CRITICAL | Demo unsafe | Stop and recover |

---

## Problem: Backend Server Not Running

### Symptom
- `python demo_check.py` shows "✗ Backend Reachable" FAILED
- Error: "Connection refused" or "Cannot connect"

### Solution

**Step 1: Check if backend process is running**
```powershell
# Windows PowerShell
Get-Process python | Where-Object { $_.CommandLine -like "*main.py*" }
```

If no process found, proceed to Step 2.

**Step 2: Start the backend**
```bash
cd c:\Users\user11\Desktop\"News AI"\Task2-master\unified_tools_backend
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Step 3: Verify startup**
- Wait 30 seconds for server to initialize
- Check console for "Uvicorn running on http://0.0.0.0:8000"
- Run: `curl http://localhost:8000/health`
- Should return JSON response

**Step 4: Re-run demo check**
```bash
python demo_check.py
```

---

## Problem: Backend Running but Returning Errors

### Symptom
- Backend reachable, but endpoints return errors
- `demo_check.py` shows "✗ Backend Health" or "✗ Pipeline Endpoint" FAILED
- Error messages: HTTP 500, timeouts, or service unavailable

### Solution

**Step 1: Check backend logs**
- Look at the terminal where backend is running
- Look for error messages like:
  - `ImportError` → Missing dependencies
  - `ModuleNotFoundError` → Python packages missing
  - `Connection refused` → Services (LLM, database) unavailable

**Step 2: Verify dependencies are installed**
```bash
cd unified_tools_backend
pip list | findstr -E "fastapi|requests|beautifulsoup"
```

If missing packages, reinstall:
```bash
pip install -r requirements.txt
```

**Step 3: Restart backend**
```bash
# Press Ctrl+C in backend terminal
# Then restart:
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Step 4: Check environment variables**
Create/verify `.env` file in `unified_tools_backend/`:
```env
BACKEND_URL=http://localhost:8000
OPENAI_API_KEY=your_key_if_needed
# Add other keys as needed
```

**Step 5: Verify connectivity to external services**
```bash
# Test if you can reach OpenAI / other APIs
python -c "import requests; print(requests.get('https://api.openai.com', timeout=5).status_code)"
```

---

## Problem: Frontend Not Responsive

### Symptom
- `demo_check.py` shows "⚠ Frontend Reachable" FAILED
- Can access backend, but UI doesn't load
- Error: "Cannot connect to frontend" or blank page

### Solution

**Step 1: Check if frontend is running**
```powershell
# Windows PowerShell
Get-Process node | Where-Object { $_.CommandLine -like "*next*" }
```

**Step 2: Start frontend**
```bash
cd c:\Users\user11\Desktop\"News AI"\Task2-master\blackhole-frontend
npm install  # If first time
npm run dev
```

**Step 3: Verify frontend started**
- Wait for "ready - started server on"
- Navigate to `http://localhost:3000` in browser
- Should see News AI dashboard

**Step 4: Verify backend connectivity from frontend**
- Open browser console (F12)
- Check Network tab when performing an action
- Should see requests to `http://localhost:8000/api/*`
- If requests fail, check CORS in backend (may need to allow frontend origin)

---

## Problem: Monitoring Script Crashes

### Symptom
- `monitor_backend.py` exits with error
- Error messages: `ModuleNotFoundError`, `HTTPError`, etc.

### Solution

**Step 1: Verify Python version**
```bash
python --version  # Should be 3.9+
```

**Step 2: Install required packages**
```bash
pip install requests
pip install python-dotenv
```

**Step 3: Restart monitoring**
```bash
cd c:\Users\user11\Desktop\"News AI"\Task2-master
python monitor_backend.py --backend http://localhost:8000
```

---

## Problem: Demo Safety Checker Reports UNSAFE

### Symptom
- `python demo_check.py` returns exit code 1 (UNSAFE)
- Output shows red X's (✗) on critical checks

### Solutions

**If "Backend Reachability" fails:**
- See "Backend Server Not Running" section above

**If "Backend Health" fails:**
- See "Backend Running but Returning Errors" section
- Check backend logs for errors

**If "Pipeline Endpoint" fails:**
- Check if `/api/unified-news-workflow` is defined in `main.py`
- Restart backend (pipeline code may not have reloaded)

**If "Processing Endpoint" fails:**
- One or more of: scraping, summarization services offline
- Check external API connectivity (for OpenAI, etc.)
- Verify `.env` has correct API keys

**If "Frontend Reachability" fails (WARNING only):**
- Frontend is optional; backend must be running
- Demo can proceed with backend only if needed

---

## Demo Safety Matrix

| Scenario | Safe? | Action |
|----------|-------|--------|
| Backend ✓, Frontend ✓ | YES | Proceed normally |
| Backend ✓, Frontend ✗ | YES | Use API testing; skip UI demo if needed |
| Backend ✗, any | NO | STOP - Fix backend first |
| Pipeline endpoint down | NO | STOP - Check logs |
| Minor latency degradation | YES | Monitor; may be slow |

---

## Real-Time Monitoring During Demo

### Start monitoring before demo begins:

```bash
# Terminal 1: Backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (optional)
npm run dev

# Terminal 3: Monitoring (KEEP RUNNING)
python monitor_backend.py --backend http://localhost:8000 --interval 30
```

### What to watch for during demo:

- **Green checkmarks (✓)** – System healthy
- **Yellow warnings (⚠)** – Slow but functional
- **Red X's (✗)** – Demo likely to fail; have backup
- **Latency spike** – Slow operations; pre-warn audience

### If something fails during demo:

1. **Continue presenting** if endpoint recovers quickly
2. **Acknowledge slowness** to audience ("Just running live, might be a bit slow...")
3. **Have backup data ready** – Pre-recorded examples or screenshots
4. **Check error log** after demo: `newsai_error_log.json`

---

## Logs & Diagnostics

### View error log:
```bash
type newsai_error_log.json
# or with Python:
python -c "import json; print(json.dumps(json.load(open('newsai_error_log.json')), indent=2))"
```

### Generate monitoring report:
```bash
python monitor_backend.py --backend http://localhost:8000 --iterations 5 --report
```

### Check backend logs:
- Look at terminal where backend is running
- Ctrl+F for "ERROR", "CRITICAL", "Exception"
- Note timestamps to correlate with demo issues

---

## Quick Restart Sequence

If everything breaks:

```powershell
# 1. Kill all running processes
$backend = Get-Process python | Where-Object { $_.CommandLine -like "*main.py*" }
$frontend = Get-Process node | Where-Object { $_.CommandLine -like "*next*" }
if ($backend) { $backend | Stop-Process -Force }
if ($frontend) { $frontend | Stop-Process -Force }

# 2. Wait 5 seconds
Start-Sleep -Seconds 5

# 3. Start fresh (in separate terminals):
# Terminal A:
cd "c:\Users\user11\Desktop\News AI\Task2-master\unified_tools_backend"
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal B (optional):
cd "c:\Users\user11\Desktop\News AI\Task2-master\blackhole-frontend"
npm run dev

# Terminal C (monitor):
cd "c:\Users\user11\Desktop\News AI\Task2-master"
python monitor_backend.py

# 4. Wait 30 seconds

# 5. Run safety check
python demo_check.py
```

---

## Common Error Messages & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ConnectionRefusedError` | Backend not running | Start backend with uvicorn |
| `ModuleNotFoundError: fastapi` | Dependencies missing | `pip install -r requirements.txt` |
| `Timeout waiting for response` | Backend slow or hanging | Restart backend, check logs |
| `CORS error in browser` | Frontend-backend mismatch | Check frontend `.env.local` |
| `405 Method Not Allowed` | Wrong HTTP verb | Ensure POST vs GET correct |
| `422 Validation Error` | Bad request payload | Check endpoint documentation |

---

## Support Information

- **Backend docs**: `unified_tools_backend/main.py` (Swagger: http://localhost:8000/docs)
- **Frontend docs**: `blackhole-frontend/` (Next.js 14)
- **Architecture**: `README.md` in project root
- **API endpoints**: `main.py` source code (search `@app.post`, `@app.get`)

---

## Demo Readiness Checklist

Before demoing, verify:

- [ ] Backend running (`python -m uvicorn main:app ...`)
- [ ] Frontend running (`npm run dev`)
- [ ] Safety check passed (`python demo_check.py` returns SAFE)
- [ ] Monitor running in background (`python monitor_backend.py`)
- [ ] API keys in `.env` (if needed)
- [ ] Database initialized (if needed)
- [ ] Test data loaded
- [ ] Error log being written to (`newsai_error_log.json` exists)

---

**Last Updated**: March 4, 2026  
**Version**: 1.0  
**Demo System**: Blackhole Infiverse – News AI
