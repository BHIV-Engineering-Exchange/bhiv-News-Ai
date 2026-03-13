# Insight Node - Deployment & Demo Guide

## 1. Deployment (Render.com)

This service is configured for **Render** (Web Service).

### Build Configuration
- **Repo**: `https://github.com/your-repo/news-ai-backend`
- **Root Directory**: `Task2-master/unified_tools_backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Python Version**: `3.11.4` (Defined in `runtime.txt`)

### Environment Variables
| Key | Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.11.4` | Ensure consistent runtime |
| `OPENAI_API_KEY` | `sk-...` | Required for Summarization |
| `SERPER_API_KEY` | `...` | Required for Vetting |
| `YOUTUBE_API_KEY`| `...` | Required for Video Search |

## 2. Demo Limits & Latency (The "Golden Path")

During the live demo, adhere to these constraints to avoid timeouts:

- **Max URL Length**: 2000 chars.
- **Expected Latency**:
  - Scraping: ~2-4s
  - Vetting: ~3-5s
  - Summarization: ~2-4s
  - **Total Pipeline**: **~8-12 seconds**
- **Video Search**:
  - The system has an **8-second timeout** for video search.
  - If YouTube API is slow, it will fall back to "Simple Fallback" mode (showing generic related videos). This is normal behavior.

## 3. Failure Behavior (What to expect)

- **If Scraping Fails**: The pipeline stops immediately. Error is shown in Frontend.
- **If Vetting Fails**: Returns `authenticity_score: 0`. Frontend shows "Unknown Credibility".
- **If Video Search Fails**: Sidebar shows fallback videos. **The main analysis will still succeed.**

## 4. Verification Checklist (Before going live)

- [ ] Run `start_production.bat` locally.
- [ ] Hit `/health` endpoint: `curl http://localhost:8001/health`
- [ ] Verify `api_keys_configured` in health response are all `true`.
- [ ] Run one full test via Frontend (`http://localhost:3002`).

**Status**: READY FOR DEPLOYMENT
**Tag**: `insight-demo-stable-v1`

## 5. Insight Node Specifics (Sankalp)

### 📊 Latency Expectations
- **Scraping**: 2-5 seconds (varies by site).
- **Vetting**: 1-2 seconds (AI analysis).
- **Summarization**: 2-3 seconds.
- **Total Workflow**: Expect **8-15 seconds** for a full result.

### 🛑 Known Limits
- **Twitter/X**: Direct scraping may fail without API keys. Fallback to "General News" search is active.
- **Paywalls**: WSJ/NYT may return limited content. This is expected behavior.
- **Audio Generation**: TTS is generated on-demand. First play may take 1-2s to buffer.

### 🛡️ Failure Discipline
- If **Scraping Fails**: The system will **NOT** return a mock article. It will show a "Scraping Failed" error. This is intentional for production transparency.
- If **Vetting Fails**: Authenticity score will show "N/A" or "Unknown" rather than guessing.

### 🎥 Video Search
- Videos are fetched from **YouTube** (primary) and **Twitter** (secondary).
- If no exact match is found, the system performs a broader topic search to ensure the sidebar is never empty.
