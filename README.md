# 🕳️ Blackhole Infiverse LLP – News AI

Advanced AI-powered news analysis platform that ingests live articles, verifies credibility, summarizes content, locates related video coverage, and exposes the results through a Next.js dashboard plus a FastAPI backend.

---

## ✨ Features

- **Unified Workflow** – Scraping → Vetting → Summarization → Video discovery, orchestrated from a single `/api/unified-news-workflow` endpoint.
- **Rich Frontend** – Next.js 14 (App Router) UI with real-time workflow feedback, video sidebar, analytics, and saved news feed.
- **Persistent News Feed** – Scraped articles are cached locally/on-disk (`blackhole-frontend/data/scraped-news.json`) and surfaced on the News Feed page with categories, images, and related videos.
- **YouTube Integration** – Client-side iframe management with custom controls (play/pause/next) powered by the YouTube IFrame API.
- **AI Tooling Hooks** – Ready to connect to AI services for summarization, credibility scoring, and video generation.

---

## 🗂️ Repository Structure

```
v1 News AI/
├── blackhole-frontend/           # Next.js 14 + TypeScript frontend
│   ├── app/                      # App Router pages (home, feed, API routes)
│   ├── components/               # Reusable UI components (VideoPlayer, News cards, etc.)
│   ├── data/scraped-news.json    # Local cache of scraped articles
│   ├── lib/                      # API helpers, storage utilities
│   └── README.md                 # Frontend-specific documentation
├── unified_tools_backend/        # FastAPI backend + scraping pipeline
│   ├── main.py                   # Unified workflow + scraping/video services
│   └── requirements.txt          # Backend dependencies
└── README.md                     # ← You are here
```

---

## 🧰 Requirements

| Component  | Minimum Version | Notes                                   |
|------------|-----------------|-----------------------------------------|
| Node.js    | 18.x            | Tested with `v22.21.0`                  |
| npm        | 9.x             | Bundled with Node                       |
| Python     | 3.9+            | Tested with `python 3.14.0`             |
| Git        | 2.4+            | For version control                     |
| OS         | Windows 10+     | Scripts target PowerShell/CMD           |

> ⚠️ The YouTube iframe requires client-side rendering. Make sure you run the frontend in a real browser (not server-side only environments).

---

## 🚀 Getting Started

### 1. Clone & Install

```bash
git clone <REPO_URL> "v1 News AI"
cd "v1 News AI"
```

Install backend deps:

```bash
cd unified_tools_backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```

Install frontend deps:

```bash
cd ../blackhole-frontend
npm install
```

### 2. Environment Variables

Create `.env` files as needed:

- `unified_tools_backend/.env` – API keys for scraping, OpenAI, etc.
- `blackhole-frontend/.env.local` – Frontend-specific overrides. By default the frontend talks to `http://localhost:8000`.

Refer to `blackhole-frontend/README.md` for the exhaustive list of env keys.

---

## ▶️ Running Locally

### Backend (FastAPI + Uvicorn)

```bash
cd unified_tools_backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access:
- API root: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### Frontend (Next.js)

```bash
cd blackhole-frontend
npm run dev
```

Access UI at `http://localhost:3000`.

> 💡 Windows helper scripts: `start_server.bat` (backend) and `start_frontend_debug.bat` (frontend) capture logs if you need persistent output.

---

## 🧪 Testing & QA

| Area                | Command                         | Notes                                                         |
|---------------------|---------------------------------|---------------------------------------------------------------|
| Frontend lint       | `npm run lint`                  | Uses Next.js/ESLint config.                                   |
| Backend smoke test  | `pytest` *(if tests added)*     | Not included yet—recommend adding tests around scrapers.      |
| Manual QA           | Browser (Chrome/Edge)           | Verify hydration warnings are gone + feed updates correctly.  |

Hydration safeguards are in place for the YouTube iframe. If you see hydration warnings, ensure the component renders only on the client (see `VideoPlayer.tsx`).

---

## 📦 Deployment Tips

1. **Backend** – Deploy FastAPI via Uvicorn/Gunicorn behind a reverse proxy (Azure App Service, AWS ECS, etc.). Persist `scraped-news.json` to a shared store (S3/Azure Blob) if you need multi-instance support.
2. **Frontend** – Build with `npm run build` and deploy to Vercel, Azure Static Web Apps, or another Node-capable host. Configure the env var `NEXT_PUBLIC_API_BASE` if the backend runs on a different domain.
3. **CORS** – `main.py` currently allows `http://localhost:3000` and wildcard origins for dev. Lock this down for production.

---

## 🛠️ Troubleshooting

| Symptom                                  | Fix                                                                 |
|------------------------------------------|----------------------------------------------------------------------|
| `ERR_BLOCKED_BY_CLIENT` for YouTube logs | Expected if an ad blocker blocks YouTube analytics; safe to ignore. |
| Hydration error (`iframe mismatch`)      | Fixed by client-only mount in `VideoPlayer`; ensure no SSR fallback. |
| Articles not showing in News Feed        | Check browser console; ensure `saveScrapedNews` logs show success.  |
| Backend refuses connections              | Confirm Python env active, required env vars available, port 8000 free. |

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-change`
2. Commit with context: `git commit -m "Describe fix"`
3. Submit a PR describing the change, test plan, and screenshots if UI-visible.

---

## 📫 Support

Have questions or need access to API keys? Reach out to the Blackhole Infiverse LLP core team or open an issue in the GitHub repo.

---

Happy hacking! 🌀

