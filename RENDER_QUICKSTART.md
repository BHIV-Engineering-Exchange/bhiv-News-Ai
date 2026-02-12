# 🚀 Render Deployment - Quick Start

Deploy your News AI application to Render in minutes!

## 📋 What You'll Need

- GitHub account
- Render account (free tier available at [render.com](https://render.com))
- Your code pushed to a GitHub repository

## ⚡ Quick Deploy (5 minutes)

### Step 1: Push to GitHub

```bash
# If not already initialized
git init
git add .
git commit -m "Ready for Render deployment"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy on Render

**Option A: One-Click Blueprint Deploy** (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render detects `render.yaml` automatically
5. Click **"Apply"** - Done! ✨

**Option B: Manual Deploy**

See `RENDER_DEPLOYMENT.md` for detailed manual setup instructions.

### Step 3: Get Your URLs

After deployment completes (5-10 minutes):

- **Backend**: `https://news-ai-backend.onrender.com`
- **Frontend**: `https://news-ai-frontend.onrender.com`
- **API Docs**: `https://news-ai-backend.onrender.com/docs`

### Step 4: Update CORS (Important!)

Once you have your frontend URL, update CORS settings:

```bash
cd unified_tools_backend
python update_cors.py https://YOUR-FRONTEND-URL.onrender.com
git add main.py
git commit -m "Update CORS for production"
git push
```

Render will auto-redeploy the backend.

## ✅ Verify Deployment

1. **Backend Health**: Visit `https://YOUR-BACKEND.onrender.com/health`
   - Should show: `{"status": "healthy", ...}`

2. **Frontend**: Visit `https://YOUR-FRONTEND.onrender.com`
   - Dashboard should load

3. **Test Workflow**: Enter a news URL and click "Analyze"

## 🎯 Your Deployment URLs

After deployment, save these URLs:

```
Backend:  https://news-ai-backend.onrender.com
Frontend: https://news-ai-frontend.onrender.com
API Docs: https://news-ai-backend.onrender.com/docs
Health:   https://news-ai-backend.onrender.com/health
```

## 📁 Files Created for Deployment

- ✅ `render.yaml` - Blueprint configuration
- ✅ `RENDER_DEPLOYMENT.md` - Detailed deployment guide
- ✅ `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- ✅ `unified_tools_backend/Procfile` - Process configuration
- ✅ `unified_tools_backend/build.sh` - Build script
- ✅ `unified_tools_backend/.env.production.example` - Environment variables template
- ✅ `unified_tools_backend/update_cors.py` - CORS update utility

## 🔧 Configuration

### Backend Environment Variables

Set these in Render Dashboard → Backend Service → Environment:

```
PYTHON_VERSION=3.11.0
ENABLE_OPENAI=0
ENABLE_GROK=0
OLLAMA_BASE_URL=https://249b3496e9d6.ngrok-free.app
OLLAMA_MODEL=llama3.1
BLACKHOLE_LLM_URL=https://d52770bec07e.ngrok-free.app
BLACKHOLE_LLM_MODEL=llama3.1
```

### Frontend Environment Variables

These are auto-configured in `render.yaml`:

```
NEXT_PUBLIC_NOOPUR_API_BASE=[Backend URL]
NEXT_PUBLIC_SANKALP_API_BASE=[Backend URL]
NEXT_PUBLIC_SEEYA_API_BASE=[Backend URL]
NEXT_PUBLIC_ENV=production
```

## 💡 Tips

### Free Tier Limitations

- Services sleep after 15 min of inactivity
- First request after sleep takes 30-60 seconds
- 750 hours/month of runtime per service
- 100GB bandwidth/month

### Keeping Services Awake

To prevent cold starts, you can:
1. Upgrade to paid tier ($7/month per service)
2. Use a service like [UptimeRobot](https://uptimerobot.com) to ping your app every 14 minutes
3. Accept the cold start delay (acceptable for most use cases)

### Adding API Keys Later

1. Go to Render Dashboard
2. Select your backend service
3. Click "Environment" tab
4. Add key-value pairs:
   - `OPENAI_API_KEY`
   - `GROK_API_KEY`
   - `SERPER_API_KEY`
   - `YOUTUBE_API_KEY`
   - `TWITTER_BEARER_TOKEN`
5. Service auto-redeploys

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check logs in Render Dashboard, verify dependencies |
| CORS errors | Run `update_cors.py` with your frontend URL |
| Service won't start | Check environment variables, review logs |
| 404 errors | Verify API endpoints match between frontend/backend |
| Slow first load | Normal for free tier (cold start) |

## 📚 Documentation

- **Detailed Guide**: See `RENDER_DEPLOYMENT.md`
- **Checklist**: See `DEPLOYMENT_CHECKLIST.md`
- **Render Docs**: [render.com/docs](https://render.com/docs)

## 🔄 Updating Your App

Render auto-deploys on git push:

```bash
# Make your changes
git add .
git commit -m "Update feature X"
git push
```

Both services rebuild automatically!

## 🎉 You're Done!

Your News AI app is now live on Render. Share your frontend URL with others!

---

**Need help?** Check the detailed guides or Render's documentation.
