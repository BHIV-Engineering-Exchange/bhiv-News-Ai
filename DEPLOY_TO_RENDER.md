# 🚀 Deploy to Render - Complete Guide

## 📦 What's Ready

Your News AI application is **fully configured** for Render deployment! All necessary files have been created.

## 🎯 Deployment Files Created

### Core Configuration
- ✅ **`render.yaml`** - One-click Blueprint deployment config
- ✅ **`deploy-to-render.bat`** - Windows helper script

### Backend Files
- ✅ **`unified_tools_backend/Procfile`** - Process configuration
- ✅ **`unified_tools_backend/build.sh`** - Build script
- ✅ **`unified_tools_backend/.env.production.example`** - Environment template
- ✅ **`unified_tools_backend/update_cors.py`** - CORS update utility

### Documentation
- ✅ **`RENDER_QUICKSTART.md`** - 5-minute quick start
- ✅ **`RENDER_DEPLOYMENT.md`** - Detailed deployment guide
- ✅ **`DEPLOYMENT_CHECKLIST.md`** - Step-by-step checklist
- ✅ **`DEPLOYMENT_SUMMARY.md`** - Overview and reference

## 🚀 Three Ways to Deploy

### Option 1: Automated Script (Easiest for Windows)

```bash
# Run the helper script
deploy-to-render.bat
```

This will:
1. Initialize git (if needed)
2. Commit your changes
3. Show you next steps

### Option 2: Blueprint Deploy (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push
   ```

2. **Deploy on Render:**
   - Go to https://dashboard.render.com
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Render detects `render.yaml` automatically
   - Click **"Apply"**
   - Wait 5-10 minutes ☕

3. **Update CORS:**
   ```bash
   cd unified_tools_backend
   python update_cors.py https://YOUR-FRONTEND-URL.onrender.com
   git add main.py
   git commit -m "Update CORS for production"
   git push
   ```

### Option 3: Manual Setup

See `RENDER_DEPLOYMENT.md` for detailed manual setup instructions.

## 📋 Step-by-Step Checklist

### Before Deployment

- [ ] Review `render.yaml` configuration
- [ ] Ensure code is working locally
- [ ] Have GitHub account ready
- [ ] Have Render account ready (free tier available)

### GitHub Setup

- [ ] Create new repository on GitHub
- [ ] Copy repository URL
- [ ] Run:
  ```bash
  git remote add origin YOUR_REPO_URL
  git add .
  git commit -m "Prepare for Render deployment"
  git push -u origin main
  ```

### Render Deployment

- [ ] Go to https://dashboard.render.com
- [ ] Click "New +" → "Blueprint"
- [ ] Connect GitHub repository
- [ ] Click "Apply"
- [ ] Wait for deployment (5-10 minutes)
- [ ] Note your URLs:
  - Backend: `https://news-ai-backend.onrender.com`
  - Frontend: `https://news-ai-frontend.onrender.com`

### Post-Deployment

- [ ] Update CORS with frontend URL
- [ ] Test backend health: `/health`
- [ ] Test frontend loads
- [ ] Test news analysis workflow
- [ ] Verify video playback
- [ ] Check API docs: `/docs`

## 🔧 Configuration Details

### Backend Service

**Runtime:** Python 3.11
**Build Command:** `pip install -r requirements.txt`
**Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
**Health Check:** `/health`

**Environment Variables:**
```
PYTHON_VERSION=3.11.0
ENABLE_OPENAI=0
ENABLE_GROK=0
OLLAMA_BASE_URL=https://249b3496e9d6.ngrok-free.app
OLLAMA_MODEL=llama3.1
BLACKHOLE_LLM_URL=https://d52770bec07e.ngrok-free.app
BLACKHOLE_LLM_MODEL=llama3.1
```

### Frontend Service

**Runtime:** Node 18
**Build Command:** `npm install && npm run build`
**Start Command:** `npm start`

**Environment Variables:**
```
NODE_VERSION=18.17.0
NEXT_PUBLIC_NOOPUR_API_BASE=[Auto-linked to backend]
NEXT_PUBLIC_SANKALP_API_BASE=[Auto-linked to backend]
NEXT_PUBLIC_SEEYA_API_BASE=[Auto-linked to backend]
NEXT_PUBLIC_ENV=production
```

## 💡 Important Notes

### Free Tier Limitations

- Services sleep after 15 minutes of inactivity
- First request after sleep: 30-60 seconds (cold start)
- 750 hours/month runtime per service
- 100GB/month bandwidth

### Adding API Keys (Optional)

To enable additional features, add these in Render Dashboard → Environment:

```
OPENAI_API_KEY=your_key_here
GROK_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
TWITTER_BEARER_TOKEN=your_token_here
```

Service will auto-redeploy when you add variables.

## 🎯 After Deployment

### Your Live URLs

Save these for reference:

```
Frontend:  https://news-ai-frontend.onrender.com
Backend:   https://news-ai-backend.onrender.com
API Docs:  https://news-ai-backend.onrender.com/docs
Health:    https://news-ai-backend.onrender.com/health
```

### Testing Your Deployment

1. **Health Check:**
   ```bash
   curl https://news-ai-backend.onrender.com/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Frontend:**
   - Visit your frontend URL
   - Dashboard should load
   - Try analyzing a news article

3. **API Documentation:**
   - Visit `/docs` endpoint
   - Interactive API documentation

## 🔄 Updating Your App

Render auto-deploys on git push:

```bash
# Make your changes
git add .
git commit -m "Update feature X"
git push
```

Both services rebuild automatically!

## 🐛 Troubleshooting

### Build Fails

1. Check logs in Render Dashboard
2. Verify `requirements.txt` and `package.json`
3. Check Python/Node versions

### CORS Errors

```bash
cd unified_tools_backend
python update_cors.py https://YOUR-FRONTEND-URL.onrender.com
git add main.py
git commit -m "Update CORS"
git push
```

### Service Won't Start

1. Check environment variables are set
2. Review logs in Render Dashboard
3. Verify start command is correct

### 404 Errors

1. Check API endpoints match between frontend/backend
2. Verify backend is running (check health endpoint)
3. Check frontend environment variables

### Slow First Load

This is normal for free tier (cold start). Service wakes up in 30-60 seconds.

## 📚 Documentation Reference

- **Quick Start:** `RENDER_QUICKSTART.md` (fastest path)
- **Full Guide:** `RENDER_DEPLOYMENT.md` (detailed instructions)
- **Checklist:** `DEPLOYMENT_CHECKLIST.md` (track progress)
- **Summary:** `DEPLOYMENT_SUMMARY.md` (overview)

## 💰 Cost

**Free Tier:** $0/month
- Perfect for testing and personal projects
- Includes both backend and frontend
- No credit card required

**Paid Tier:** $7/month per service
- Always-on (no cold starts)
- Better performance
- Priority support

## 🎉 Ready to Deploy!

Everything is configured. Choose your deployment method above and get started!

**Estimated Time:** 15-20 minutes (including build time)

---

**Need Help?**
- Check `RENDER_QUICKSTART.md` for fastest deployment
- See `RENDER_DEPLOYMENT.md` for detailed guide
- Visit https://render.com/docs for Render documentation
