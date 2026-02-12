# 🚀 Complete Render Deployment Guide
# Frontend + Backend Services

This guide covers deploying both your frontend and backend services to Render.

---

## 📦 What We're Deploying

1. **Frontend (Next.js)** - Blackhole Frontend
2. **Backend Services**:
   - Noopur API (Node.js/Express)
   - Sankalp API (Python/FastAPI)

---

## 🎯 Deployment Strategy

### Option A: Deploy All Services Separately (Recommended)

Deploy each service as a separate Render Web Service. This gives you:
- ✅ Independent scaling
- ✅ Better isolation
- ✅ Easier debugging
- ✅ More control

### Option B: Monorepo Deployment

Deploy from a single repository with multiple services defined in `render.yaml`.

---

## 📝 Step-by-Step Deployment

### Step 1: Deploy Backend Services First

#### 1.1 Deploy Noopur Backend (Node.js)

1. **Go to Render Dashboard** → New + → Web Service
2. **Connect Repository** containing your backend
3. **Configure:**
   ```
   Name: blackhole-noopur-api
   Region: Singapore (same as frontend)
   Root Directory: news-ai-final-backend (or your backend path)
   Runtime: Node
   Build Command: npm install
   Start Command: npm start
   ```

4. **Environment Variables:**
   ```env
   NODE_ENV=production
   PORT=3001
   DATABASE_URL=<your-database-url>
   # Add other required variables
   ```

5. **Deploy** and note the URL (e.g., `https://blackhole-noopur-api.onrender.com`)

#### 1.2 Deploy Sankalp Backend (Python)

1. **New Web Service** on Render
2. **Configure:**
   ```
   Name: blackhole-sankalp-api
   Region: Singapore
   Root Directory: unified_tools_backend (or your path)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Variables:**
   ```env
   PYTHON_VERSION=3.11
   # Add your API keys and other variables
   ```

4. **Deploy** and note the URL (e.g., `https://blackhole-sankalp-api.onrender.com`)

### Step 2: Deploy Frontend

Now that backends are deployed, deploy the frontend with the correct API URLs.

1. **New Web Service** on Render
2. **Connect** your frontend repository
3. **Configure:**
   ```
   Name: blackhole-frontend
   Region: Singapore
   Root Directory: blackhole-frontend (if in subdirectory)
   Runtime: Node
   Build Command: chmod +x build.sh && ./build.sh
   Start Command: npm start
   ```

4. **Environment Variables:**
   ```env
   NODE_ENV=production
   
   # Supabase
   NEXT_PUBLIC_SUPABASE_URL=https://pihfretaiaaammcwihes.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   
   # Database
   DATABASE_URL=postgresql://postgres.pihfretaiaaammcwihes:Somsid%40201421@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true
   
   # Backend APIs (use the URLs from Step 1)
   NEXT_PUBLIC_NOOPUR_API_BASE=https://blackhole-noopur-api.onrender.com
   NEXT_PUBLIC_SANKALP_API_BASE=https://blackhole-sankalp-api.onrender.com
   ```

5. **Deploy!**

---

## 🔧 Using render.yaml for Multi-Service Deployment

If you want to deploy all services from one configuration:

### Create render.yaml in your root directory:

```yaml
services:
  # Frontend Service
  - type: web
    name: blackhole-frontend
    env: node
    region: singapore
    plan: free
    rootDir: blackhole-frontend
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: NEXT_PUBLIC_SUPABASE_URL
        sync: false
      - key: NEXT_PUBLIC_SUPABASE_ANON_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: NEXT_PUBLIC_NOOPUR_API_BASE
        value: https://blackhole-noopur-api.onrender.com
      - key: NEXT_PUBLIC_SANKALP_API_BASE
        value: https://blackhole-sankalp-api.onrender.com

  # Noopur Backend Service
  - type: web
    name: blackhole-noopur-api
    env: node
    region: singapore
    plan: free
    rootDir: news-ai-final-backend
    buildCommand: npm install
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: 3001
      - key: DATABASE_URL
        sync: false

  # Sankalp Backend Service
  - type: web
    name: blackhole-sankalp-api
    env: python
    region: singapore
    plan: free
    rootDir: unified_tools_backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
```

Then deploy via:
1. Render Dashboard → New + → Blueprint
2. Connect repository
3. Render detects `render.yaml` and creates all services

---

## 🔐 Environment Variables Reference

### Frontend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NODE_ENV` | Environment mode | `production` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGc...` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `NEXT_PUBLIC_NOOPUR_API_BASE` | Noopur backend URL | `https://api.onrender.com` |
| `NEXT_PUBLIC_SANKALP_API_BASE` | Sankalp backend URL | `https://api2.onrender.com` |

### Backend Variables (Noopur)

| Variable | Description |
|----------|-------------|
| `NODE_ENV` | Environment mode |
| `PORT` | Server port (Render provides this) |
| `DATABASE_URL` | Database connection |
| `JWT_SECRET` | JWT signing key |
| `CORS_ORIGIN` | Allowed frontend URLs |

### Backend Variables (Sankalp)

| Variable | Description |
|----------|-------------|
| `PYTHON_VERSION` | Python version |
| `API_KEYS` | External API keys |
| `DATABASE_URL` | Database connection |

---

## 🔄 CORS Configuration

**Important:** Update backend CORS settings to allow your Render frontend domain.

### Node.js Backend (Noopur):

```javascript
// In your Express app
const cors = require('cors');

const allowedOrigins = [
  'https://blackhole-frontend.onrender.com',
  'http://localhost:3000', // for local development
];

app.use(cors({
  origin: function(origin, callback) {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
}));
```

### Python Backend (Sankalp):

```python
# In your FastAPI app
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://blackhole-frontend.onrender.com",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 Testing Your Deployment

### 1. Test Backend Services

```bash
# Test Noopur API
curl https://blackhole-noopur-api.onrender.com/health

# Test Sankalp API
curl https://blackhole-sankalp-api.onrender.com/health
```

### 2. Test Frontend

1. Visit `https://blackhole-frontend.onrender.com`
2. Open browser DevTools → Network tab
3. Verify API calls are going to correct backend URLs
4. Check for CORS errors
5. Test all features

---

## 📊 Monitoring All Services

### Render Dashboard

Monitor each service:
- CPU/Memory usage
- Request logs
- Error rates
- Deployment history

### Set Up Alerts

For each service:
1. Go to Settings → Health & Alerts
2. Configure health check paths
3. Set up email/Slack notifications

---

## 💰 Cost Optimization

### Free Tier Limits

Each free service:
- 750 hours/month
- Spins down after 15 min inactivity
- 512 MB RAM

### Recommendations

1. **Start with Free Tier** for all services
2. **Upgrade Critical Services** first:
   - Frontend → $7/month (always on)
   - Most-used backend → $7/month
3. **Keep less-used services on free tier**

### Cost Estimate

| Configuration | Monthly Cost |
|---------------|--------------|
| All Free | $0 |
| Frontend Paid | $7 |
| Frontend + 1 Backend Paid | $14 |
| All Paid | $21 |

---

## 🐛 Troubleshooting Multi-Service Setup

### Frontend Can't Connect to Backend

**Symptoms:** API calls fail, CORS errors

**Solutions:**
1. Verify backend URLs in frontend env vars
2. Check backend CORS configuration
3. Ensure backends are running (not spun down)
4. Test backend health endpoints directly

### Backend Database Connection Issues

**Symptoms:** 500 errors, connection timeouts

**Solutions:**
1. Verify DATABASE_URL format
2. Check Supabase connection pooler settings
3. Ensure SSL mode is enabled
4. Test connection from backend logs

### Services Spinning Down

**Symptoms:** First request takes 30-60 seconds

**Solutions:**
1. Upgrade to paid plan ($7/month per service)
2. Use external monitoring to ping services
3. Implement health check endpoints

---

## ✅ Complete Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to GitHub/GitLab
- [ ] All environment variables documented
- [ ] Database migrations ready
- [ ] CORS configured in backends
- [ ] Health check endpoints implemented

### Backend Deployment
- [ ] Noopur backend deployed
- [ ] Sankalp backend deployed
- [ ] Backend health checks passing
- [ ] Database connections verified
- [ ] API endpoints tested

### Frontend Deployment
- [ ] Frontend deployed with correct backend URLs
- [ ] All pages loading
- [ ] API integrations working
- [ ] Supabase authentication functional
- [ ] No CORS errors

### Post-Deployment
- [ ] Custom domains configured (if applicable)
- [ ] SSL certificates active
- [ ] Monitoring and alerts set up
- [ ] Performance tested
- [ ] Error tracking configured
- [ ] Documentation updated

---

## 🚀 Quick Start Commands

```bash
# Test local build before deploying
npm run build
npm start

# Check for build errors
npm run lint

# Test backend locally
cd news-ai-final-backend && npm start
cd unified_tools_backend && uvicorn main:app --reload
```

---

## 📞 Support Resources

- **Render Docs:** https://render.com/docs
- **Next.js on Render:** https://render.com/docs/deploy-nextjs
- **Node.js on Render:** https://render.com/docs/deploy-node-express-app
- **Python on Render:** https://render.com/docs/deploy-fastapi
- **Community:** https://community.render.com

---

## 🎉 Success!

Once all services are deployed and communicating:

1. **Share your app:** `https://blackhole-frontend.onrender.com`
2. **Monitor performance** for first 24 hours
3. **Gather feedback** from users
4. **Iterate and improve**

---

**Deployment Guide Version:** 2.0  
**Last Updated:** February 2026  
**Status:** Production Ready ✅
