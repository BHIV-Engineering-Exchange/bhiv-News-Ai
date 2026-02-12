# 🚀 Render Deployment - Quick Reference

## 📋 Pre-Flight Checklist

```bash
# 1. Ensure code is committed and pushed
git status
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Test build locally
npm run build
npm start
# Visit http://localhost:3000 to verify
```

---

## ⚡ Deploy Frontend to Render (5 Minutes)

### Method 1: Dashboard (Easiest)

1. **Go to:** https://dashboard.render.com
2. **Click:** New + → Web Service
3. **Connect:** Your GitHub repository
4. **Configure:**
   - Name: `blackhole-frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm start`
5. **Add Environment Variables:**
   ```
   NODE_ENV=production
   NEXT_PUBLIC_SUPABASE_URL=https://pihfretaiaaammcwihes.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBpaGZyZXRhaWFhYW1tY3dpaGVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0NTIzODYsImV4cCI6MjA4NjAyODM4Nn0.eF5PP22vrHh_PL627VZb28oq6L8J09Quc8E4WEfer50
   DATABASE_URL=postgresql://postgres.pihfretaiaaammcwihes:Somsid%40201421@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true
   NEXT_PUBLIC_NOOPUR_API_BASE=<your-backend-url>
   NEXT_PUBLIC_SANKALP_API_BASE=<your-backend-url>
   ```
6. **Click:** Create Web Service
7. **Wait:** 3-5 minutes for build
8. **Done!** Your app is live at `https://blackhole-frontend.onrender.com`

---

## 🔧 Environment Variables You Need

| Variable                          | Where to Get It                                        |
| --------------------------------- | ------------------------------------------------------ |
| `NEXT_PUBLIC_SUPABASE_URL`      | Already in your `.env.local`                         |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Already in your `.env.local`                         |
| `DATABASE_URL`                  | Already in your `.env.local`                         |
| `NEXT_PUBLIC_NOOPUR_API_BASE`   | Your deployed backend URL or `http://localhost:3001` |
| `NEXT_PUBLIC_SANKALP_API_BASE`  | Your deployed backend URL or `http://localhost:3002` |

---

## 🐛 Common Issues & Quick Fixes

### ❌ Build Fails

```bash
# Solution: Check logs in Render dashboard
# Common causes:
# - Missing dependencies → Check package.json
# - TypeScript errors → Run `npm run build` locally first
# - Out of memory → Upgrade to paid plan
```

### ❌ App Crashes on Start

```bash
# Solution: Check environment variables
# Verify all NEXT_PUBLIC_* variables are set
# Check Render logs for specific error
```

### ❌ API Calls Failing

```bash
# Solution: Check backend URLs
# 1. Verify NEXT_PUBLIC_NOOPUR_API_BASE is correct
# 2. Test backend directly: curl <backend-url>/health
# 3. Check CORS settings in backend
```

### ❌ Slow First Load (Free Plan)

```bash
# This is normal on free plan
# Service spins down after 15 min inactivity
# Solutions:
# 1. Upgrade to $7/month plan (always on)
# 2. Use external monitoring to ping every 10 min
```

---

## 📊 After Deployment

### ✅ Verify Everything Works

1. Visit your Render URL
2. Test all pages
3. Check browser console for errors
4. Test API integrations
5. Verify Supabase authentication

### 📈 Monitor Your App

- **Logs:** Render Dashboard → Your Service → Logs
- **Metrics:** Dashboard → Metrics tab
- **Alerts:** Settings → Health & Alerts

---

## 🔄 Update Your App

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# If auto-deploy is enabled:
# → Render automatically deploys

# If not:
# → Go to Render Dashboard → Manual Deploy
```

---

## 💰 Pricing Quick Reference

| Plan               | Cost   | Features                               |
| ------------------ | ------ | -------------------------------------- |
| **Free**     | $0     | 750 hrs/month, spins down after 15 min |
| **Starter**  | $7/mo  | Always on, 512 MB RAM                  |
| **Standard** | $25/mo | 2 GB RAM, priority support             |

**Recommendation:** Start with Free, upgrade Frontend to Starter ($7) when ready for production.

---

## 🆘 Need Help?

1. **Check logs** in Render Dashboard
2. **Read full guide:** `RENDER_DEPLOYMENT.md`
3. **Render Docs:** https://render.com/docs
4. **Community:** https://community.render.com

---

## 📱 Your URLs After Deployment

- **Frontend:** `https://blackhole-frontend.onrender.com`
- **Custom Domain:** Configure in Render → Settings → Custom Domains

---

## ⚡ Super Quick Deploy (Copy-Paste)

```bash
# 1. Push code
git push origin main

# 2. Go to Render Dashboard
# 3. New + → Web Service → Connect Repo
# 4. Copy-paste these settings:

Name: blackhole-frontend
Build: npm install && npm run build
Start: npm start

# 5. Add env vars from .env.local
# 6. Click "Create Web Service"
# 7. Done! ✅
```

---

**Last Updated:** Feb 2026 | **Status:** Ready to Deploy ✅
