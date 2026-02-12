# Vercel Deployment Guide - Blackhole Infiverse Frontend

## Prerequisites

1. ✅ Vercel CLI installed globally
2. ✅ Backend deployed and accessible (e.g., on Render)
3. ✅ GitHub repository up to date

## Quick Deployment Steps

### 1. Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate with your Vercel account.

### 2. Deploy to Preview

```bash
cd blackhole-frontend
vercel
```

This creates a preview deployment. Follow the prompts:
- **Set up and deploy?** → Yes
- **Which scope?** → Select your account
- **Link to existing project?** → No (first time)
- **Project name?** → `blackhole-infiverse-frontend` (or your choice)
- **Directory?** → `./` (current directory)
- **Override settings?** → No

### 3. Configure Environment Variables

After the first deployment, go to your Vercel Dashboard:

1. Navigate to **Project Settings** → **Environment Variables**
2. Add the following variables:

| Variable Name | Value | Environment |
|--------------|-------|-------------|
| `NEXT_PUBLIC_NOOPUR_API_BASE` | `https://your-backend.onrender.com` | Production, Preview, Development |
| `NEXT_PUBLIC_SANKALP_API_BASE` | `https://your-backend.onrender.com` | Production, Preview, Development |
| `NEXT_PUBLIC_AUDIO_BASE_URL` | `https://your-backend.onrender.com/data/audio` | Production, Preview, Development |
| `NEXT_PUBLIC_JWT_TOKEN` | `your_production_token` | Production |
| `NEXT_PUBLIC_HMAC_SECRET` | `your_production_secret` | Production |
| `NEXT_PUBLIC_ENV` | `production` | Production |

### 4. Deploy to Production

```bash
vercel --prod
```

This deploys to your production domain.

## Important Notes

### CORS Configuration

Ensure your backend (Render) allows requests from your Vercel domain:

```python
# In unified_tools_backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-app.vercel.app",
        "https://your-custom-domain.com",
        # ... other origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Domain (Optional)

1. Go to **Project Settings** → **Domains**
2. Click **Add Domain**
3. Enter your domain (e.g., `news.blackholeinfiverse.com`)
4. Update your DNS records as instructed by Vercel

### Automatic Deployments

Vercel automatically deploys:
- **Production**: When you push to `main`/`master` branch
- **Preview**: When you create a pull request

## Troubleshooting

### Build Fails

Check the build logs in Vercel Dashboard. Common issues:
- Missing environment variables
- TypeScript errors
- Dependency issues

**Solution**: Fix locally, test with `npm run build`, then push to GitHub.

### API Connection Issues

If the frontend can't connect to the backend:
1. Verify environment variables are set correctly
2. Check CORS settings on backend
3. Ensure backend is running and accessible

### Static File Issues

If audio files don't play:
1. Verify `NEXT_PUBLIC_AUDIO_BASE_URL` points to your backend
2. Ensure backend is serving static files from `/data` route
3. Check browser console for CORS errors

## Useful Commands

```bash
# View deployment logs
vercel logs

# List all deployments
vercel ls

# Remove a deployment
vercel rm [deployment-url]

# Pull environment variables locally
vercel env pull

# Link local project to Vercel project
vercel link
```

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Configure environment variables
3. ✅ Test the deployment
4. ✅ Set up custom domain (optional)
5. ✅ Enable automatic deployments from GitHub

## Support

- Vercel Docs: https://vercel.com/docs
- Next.js Deployment: https://nextjs.org/docs/deployment
