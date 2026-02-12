# 🚀 Render Deployment Guide - Blackhole Frontend

Complete step-by-step guide to deploy your Next.js frontend to Render.

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ A GitHub/GitLab account with your code pushed to a repository
- ✅ A Render account (sign up at https://render.com)
- ✅ Your environment variables ready (Supabase credentials, API URLs, etc.)
- ✅ Backend API deployed and accessible (if applicable)

---

## 🎯 Deployment Methods

### Method 1: Using Render Dashboard (Recommended for First Time)

#### Step 1: Prepare Your Repository

1. **Ensure your code is pushed to GitHub/GitLab**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify `package.json` has correct scripts**
   - ✅ `build`: `next build`
   - ✅ `start`: `next start`

#### Step 2: Create New Web Service on Render

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**

2. **Connect Your Repository**
   - Choose **GitHub** or **GitLab**
   - Authorize Render to access your repositories
   - Select your `blackhole-frontend` repository

3. **Configure Service Settings**

   | Setting | Value |
   |---------|-------|
   | **Name** | `blackhole-frontend` (or your preferred name) |
   | **Region** | Singapore / Oregon / Frankfurt (choose closest to users) |
   | **Branch** | `main` |
   | **Root Directory** | Leave empty (or specify if in subdirectory) |
   | **Runtime** | `Node` |
   | **Build Command** | `npm install && npm run build` |
   | **Start Command** | `npm start` |
   | **Plan** | Free (or paid for better performance) |

#### Step 3: Configure Environment Variables

Click **"Advanced"** and add these environment variables:

```env
# Required Variables
NODE_ENV=production

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://pihfretaiaaammcwihes.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBpaGZyZXRhaWFhYW1tY3dpaGVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0NTIzODYsImV4cCI6MjA4NjAyODM4Nn0.eF5PP22vrHh_PL627VZb28oq6L8J09Quc8E4WEfer50

# Database Connection
DATABASE_URL=postgresql://postgres.pihfretaiaaammcwihes:Somsid%40201421@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true

# Backend API URLs (Update these with your actual backend URLs)
NEXT_PUBLIC_NOOPUR_API_BASE=http://localhost:3001
NEXT_PUBLIC_SANKALP_API_BASE=http://localhost:3002
```

**⚠️ Important Notes:**
- Replace `NEXT_PUBLIC_NOOPUR_API_BASE` and `NEXT_PUBLIC_SANKALP_API_BASE` with your actual deployed backend URLs
- If you don't have backend deployed yet, you can use placeholder values and update later
- All `NEXT_PUBLIC_*` variables are exposed to the browser, so don't put secrets there

#### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build your Next.js app
   - Start the production server

3. **Monitor the deployment logs** in real-time
   - Build typically takes 3-5 minutes
   - Watch for any errors in the logs

#### Step 5: Verify Deployment

Once deployed, you'll get a URL like: `https://blackhole-frontend.onrender.com`

1. **Test the application:**
   - Visit the URL
   - Check if all pages load correctly
   - Test API connections
   - Verify Supabase integration

2. **Check for common issues:**
   - 404 errors → Check routing configuration
   - API errors → Verify environment variables
   - Build errors → Check deployment logs

---

### Method 2: Using render.yaml (Infrastructure as Code)

This method uses the `render.yaml` file already created in your project.

#### Step 1: Update render.yaml

The file is already created at `render.yaml`. Review and update if needed.

#### Step 2: Deploy via Render Dashboard

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your repository
4. Render will detect `render.yaml` and configure automatically
5. Review settings and click **"Apply"**

#### Step 3: Add Environment Variables

Even with `render.yaml`, you need to add sensitive values manually:

1. Go to your service in Render Dashboard
2. Click **"Environment"** tab
3. Add the values for each variable listed in the yaml

---

### Method 3: Using Render CLI

#### Step 1: Install Render CLI

```bash
npm install -g @render/cli
```

#### Step 2: Login

```bash
render login
```

#### Step 3: Deploy

```bash
# From your project directory
render deploy
```

---

## 🔧 Post-Deployment Configuration

### 1. Custom Domain (Optional)

1. Go to your service → **"Settings"** → **"Custom Domains"**
2. Click **"Add Custom Domain"**
3. Enter your domain (e.g., `news.yourdomain.com`)
4. Update your DNS records:
   ```
   Type: CNAME
   Name: news (or @)
   Value: [provided by Render]
   ```
5. Wait for DNS propagation (can take up to 48 hours)
6. Render will automatically provision SSL certificate

### 2. Auto-Deploy on Git Push

1. Go to **"Settings"** → **"Build & Deploy"**
2. Enable **"Auto-Deploy"**
3. Choose branch (usually `main`)
4. Now every push to main will trigger automatic deployment

### 3. Health Checks

Render automatically monitors your service. Configure custom health checks:

1. Go to **"Settings"** → **"Health & Alerts"**
2. Set **Health Check Path**: `/` or `/api/health`
3. Configure alert notifications

---

## 🐛 Troubleshooting Common Issues

### Build Fails with "Module not found"

**Solution:**
```bash
# Ensure all dependencies are in package.json
npm install
git add package.json package-lock.json
git commit -m "Update dependencies"
git push
```

### Application Crashes on Start

**Check logs:**
1. Go to your service → **"Logs"** tab
2. Look for error messages
3. Common causes:
   - Missing environment variables
   - Port binding issues (Render uses PORT env var)
   - Database connection errors

**Fix:**
- Verify all environment variables are set
- Check DATABASE_URL format
- Ensure Next.js is configured for production

### API Calls Failing (CORS Errors)

**Solution:**
1. Update backend CORS settings to allow your Render domain:
   ```javascript
   // Backend CORS config
   const allowedOrigins = [
     'https://blackhole-frontend.onrender.com',
     'https://your-custom-domain.com'
   ];
   ```

2. Update environment variables with correct backend URLs

### Slow Performance on Free Plan

**Free Plan Limitations:**
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Limited resources (512 MB RAM)

**Solutions:**
- Upgrade to paid plan ($7/month) for always-on service
- Use external monitoring service to ping your app every 10 minutes
- Optimize your build size

### Environment Variables Not Working

**Checklist:**
- ✅ Variables starting with `NEXT_PUBLIC_` are accessible in browser
- ✅ Server-side variables don't need `NEXT_PUBLIC_` prefix
- ✅ After adding/changing env vars, trigger a new deployment
- ✅ Check for typos in variable names

---

## 📊 Monitoring & Maintenance

### 1. View Logs

```bash
# Real-time logs in dashboard
# Or use Render CLI
render logs -f
```

### 2. Metrics

Monitor in Render Dashboard:
- CPU usage
- Memory usage
- Request count
- Response times
- Error rates

### 3. Alerts

Set up alerts for:
- Service down
- High error rates
- Memory/CPU spikes

---

## 🔄 Updating Your Deployment

### Method 1: Git Push (if Auto-Deploy enabled)

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render automatically deploys
```

### Method 2: Manual Deploy

1. Go to Render Dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

### Method 3: Rollback

If something breaks:
1. Go to **"Events"** tab
2. Find previous successful deployment
3. Click **"Rollback to this version"**

---

## 💰 Pricing Considerations

### Free Plan
- ✅ Perfect for testing and small projects
- ✅ 750 hours/month free
- ❌ Spins down after 15 min inactivity
- ❌ Limited to 512 MB RAM

### Starter Plan ($7/month)
- ✅ Always on (no spin-down)
- ✅ 512 MB RAM
- ✅ Better performance
- ✅ Custom domains

### Standard Plan ($25/month)
- ✅ 2 GB RAM
- ✅ Priority support
- ✅ Better for production apps

---

## 🔐 Security Best Practices

### 1. Environment Variables

- ✅ Never commit `.env` files to Git
- ✅ Use Render's environment variable management
- ✅ Rotate sensitive keys regularly
- ✅ Use different credentials for dev/prod

### 2. Database Security

- ✅ Use SSL connections (already in your DATABASE_URL)
- ✅ Restrict database access to Render IPs if possible
- ✅ Regular backups (Supabase handles this)

### 3. API Security

- ✅ Implement rate limiting
- ✅ Use CORS properly
- ✅ Validate all inputs
- ✅ Keep dependencies updated

---

## ✅ Deployment Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Backend APIs are accessible
- [ ] Database connection tested
- [ ] Build completes successfully
- [ ] Application starts without errors
- [ ] All pages load correctly
- [ ] API integrations working
- [ ] Supabase authentication functional
- [ ] Mobile responsiveness verified
- [ ] SSL certificate active (automatic on Render)
- [ ] Custom domain configured (if applicable)
- [ ] Monitoring and alerts set up
- [ ] Error tracking configured
- [ ] Performance tested
- [ ] SEO meta tags in place

---

## 🆘 Getting Help

### Render Support
- Documentation: https://render.com/docs
- Community: https://community.render.com
- Support: support@render.com

### Common Resources
- Next.js on Render: https://render.com/docs/deploy-nextjs
- Environment Variables: https://render.com/docs/environment-variables
- Custom Domains: https://render.com/docs/custom-domains

---

## 📝 Quick Reference Commands

```bash
# View logs
render logs -f

# Deploy manually
render deploy

# List services
render services list

# SSH into service (paid plans only)
render ssh

# View environment variables
render env list
```

---

## 🎉 Next Steps After Deployment

1. **Test thoroughly** - Click through all features
2. **Monitor performance** - Watch metrics for first 24 hours
3. **Set up analytics** - Google Analytics, Mixpanel, etc.
4. **Configure CDN** - Render includes CDN, but verify it's working
5. **Plan scaling** - Monitor usage and upgrade plan if needed
6. **Document** - Keep this guide updated with your specific configuration

---

**Last Updated:** February 2026

**Deployment Status:** Ready for Render ✅
