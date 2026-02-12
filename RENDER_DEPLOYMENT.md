# Deployment Guide for Render

This guide will help you deploy the News AI application to Render.

## Prerequisites

1. A [Render account](https://render.com) (free tier available)
2. Your GitHub repository pushed to GitHub
3. Git installed locally

## Deployment Steps

### Step 1: Push Code to GitHub

If you haven't already, push your code to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Render deployment"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Click **"Apply"** to create both services

#### Option B: Manual Setup

**Backend Service:**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `news-ai-backend`
   - **Region**: Oregon (or your preferred region)
   - **Branch**: `main`
   - **Root Directory**: `unified_tools_backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. Add Environment Variables:
   - `PYTHON_VERSION`: `3.11.0`
   - `ENABLE_OPENAI`: `0`
   - `ENABLE_GROK`: `0`
   - `OLLAMA_BASE_URL`: `https://249b3496e9d6.ngrok-free.app`
   - `OLLAMA_MODEL`: `llama3.1`
   - `BLACKHOLE_LLM_URL`: `https://d52770bec07e.ngrok-free.app`
   - `BLACKHOLE_LLM_MODEL`: `llama3.1`

6. Set Health Check Path: `/health`
7. Click **"Create Web Service"**

**Frontend Service:**

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `news-ai-frontend`
   - **Region**: Oregon (same as backend)
   - **Branch**: `main`
   - **Root Directory**: `blackhole-frontend`
   - **Runtime**: Node
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Free

4. Add Environment Variables:
   - `NODE_VERSION`: `18.17.0`
   - `NEXT_PUBLIC_NOOPUR_API_BASE`: `https://news-ai-backend.onrender.com` (use your backend URL)
   - `NEXT_PUBLIC_SANKALP_API_BASE`: `https://news-ai-backend.onrender.com`
   - `NEXT_PUBLIC_SEEYA_API_BASE`: `https://news-ai-backend.onrender.com`
   - `NEXT_PUBLIC_ENV`: `production`

5. Click **"Create Web Service"**

### Step 3: Update CORS Settings

After deployment, you need to update the backend CORS settings to allow your frontend domain.

1. Note your frontend URL (e.g., `https://news-ai-frontend.onrender.com`)
2. In your local code, update `unified_tools_backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://news-ai-frontend.onrender.com",  # Add your frontend URL
        # Add any other domains you need
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Commit and push the changes:

```bash
git add unified_tools_backend/main.py
git commit -m "Update CORS for production"
git push
```

Render will automatically redeploy the backend.

### Step 4: Verify Deployment

1. **Backend**: Visit `https://YOUR-BACKEND-URL.onrender.com/health`
   - Should return: `{"status": "healthy", ...}`

2. **Frontend**: Visit `https://YOUR-FRONTEND-URL.onrender.com`
   - The dashboard should load successfully

3. **API Docs**: Visit `https://YOUR-BACKEND-URL.onrender.com/docs`
   - FastAPI interactive documentation

## Important Notes

### Free Tier Limitations

- **Cold Starts**: Free tier services spin down after 15 minutes of inactivity. First request after inactivity may take 30-60 seconds.
- **Build Minutes**: Limited build minutes per month
- **Bandwidth**: 100GB/month outbound bandwidth

### Environment Variables

If you need to add API keys later (OpenAI, Grok, etc.):

1. Go to your service in Render Dashboard
2. Click **"Environment"** tab
3. Add the key-value pairs
4. Service will automatically redeploy

Example optional keys:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GROK_API_KEY`: Your Grok API key
- `SERPER_API_KEY`: For search functionality
- `YOUTUBE_API_KEY`: For YouTube video search
- `TWITTER_BEARER_TOKEN`: For Twitter video search

### Custom Domains

To use a custom domain:

1. Go to your service → **"Settings"** → **"Custom Domain"**
2. Add your domain
3. Update DNS records as instructed by Render

## Troubleshooting

### Build Failures

- Check build logs in Render Dashboard
- Verify `requirements.txt` and `package.json` are correct
- Ensure Python/Node versions are compatible

### Service Won't Start

- Check the logs in Render Dashboard
- Verify environment variables are set correctly
- Check that the start command is correct

### CORS Errors

- Ensure frontend URL is added to CORS allowed origins in `main.py`
- Redeploy backend after updating CORS settings

### API Connection Issues

- Verify backend URL in frontend environment variables
- Check that backend health endpoint returns 200 OK
- Ensure both services are in the same region for better performance

## Monitoring

- **Logs**: Available in Render Dashboard for each service
- **Metrics**: CPU, Memory usage visible in dashboard
- **Alerts**: Set up email notifications for service failures

## Updating Your Deployment

Render automatically deploys when you push to your connected branch:

```bash
# Make changes to your code
git add .
git commit -m "Your update message"
git push
```

Both services will rebuild and redeploy automatically.

## Support

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- Check the logs in Render Dashboard for detailed error messages
