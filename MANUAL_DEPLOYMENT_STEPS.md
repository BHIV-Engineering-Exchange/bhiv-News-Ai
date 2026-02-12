# Manual Vercel Deployment - Step by Step

## Current Status
✅ Vercel CLI installed (v50.11.0)
✅ Code pushed to GitHub
✅ Build tested and working
✅ Configuration files ready

## Step 1: Authenticate with Vercel

Open a **new terminal/PowerShell window** and run:

```powershell
cd "d:\AI NEWs frontend\blackhole-frontend"
vercel login
```

**What will happen:**
1. A browser window will open
2. Choose your login method (GitHub is recommended)
3. Authorize Vercel CLI
4. Return to terminal when you see "Success!"

## Step 2: Deploy to Preview

After successful login, run:

```powershell
vercel
```

**Answer the prompts:**

```
? Set up and deploy "d:\AI NEWs frontend\blackhole-frontend"? [Y/n]
→ Press Y

? Which scope do you want to deploy to?
→ Select your account/team

? Link to existing project? [y/N]
→ Press N (first time deployment)

? What's your project's name?
→ blackhole-infiverse-frontend (or your choice)

? In which directory is your code located?
→ ./ (just press Enter)

? Want to override the settings? [y/N]
→ Press N
```

**Deployment will start!** You'll see:
- Building...
- Deploying...
- Success! Your preview URL will be shown

## Step 3: Configure Environment Variables

1. Go to the Vercel Dashboard: https://vercel.com/dashboard
2. Click on your project: `blackhole-infiverse-frontend`
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

### Required Variables:

| Variable Name | Value | Environments |
|--------------|-------|--------------|
| `NEXT_PUBLIC_NOOPUR_API_BASE` | `https://your-backend.onrender.com` | ✅ Production ✅ Preview ✅ Development |
| `NEXT_PUBLIC_SANKALP_API_BASE` | `https://your-backend.onrender.com` | ✅ Production ✅ Preview ✅ Development |
| `NEXT_PUBLIC_AUDIO_BASE_URL` | `https://your-backend.onrender.com/data/audio` | ✅ Production ✅ Preview ✅ Development |
| `NEXT_PUBLIC_JWT_TOKEN` | `your_production_token` | ✅ Production |
| `NEXT_PUBLIC_HMAC_SECRET` | `your_production_secret` | ✅ Production |
| `NEXT_PUBLIC_ENV` | `production` | ✅ Production |

**Important:** Replace `https://your-backend.onrender.com` with your actual Render backend URL!

## Step 4: Redeploy with Environment Variables

After adding environment variables, run:

```powershell
vercel --prod
```

This will deploy to production with all environment variables.

## Step 5: Update Backend CORS

Update your backend's CORS settings to allow your Vercel domain:

In `unified_tools_backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://blackhole-infiverse-frontend.vercel.app",  # Add this
        "https://your-custom-domain.com",  # If you have one
        "*"  # Remove this in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then push to GitHub to update Render.

## Troubleshooting

### "Not Authenticated" Error
Run `vercel login` again and complete authentication in browser.

### Build Fails
Check build logs in Vercel Dashboard. Common fixes:
- Ensure all dependencies are in `package.json`
- Check for TypeScript errors
- Verify environment variables are set

### Can't Connect to Backend
1. Verify backend URL in environment variables
2. Check CORS settings on backend
3. Ensure backend is running on Render

## Quick Commands Reference

```powershell
# Login
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm [deployment-url]
```

## Next Steps After Deployment

1. ✅ Test the preview deployment
2. ✅ Configure environment variables
3. ✅ Deploy to production
4. ✅ Update backend CORS
5. ✅ Test production deployment
6. ✅ (Optional) Add custom domain

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs
- Vercel Support: https://vercel.com/support
