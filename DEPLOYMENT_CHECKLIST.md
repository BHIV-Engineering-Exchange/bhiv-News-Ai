# Quick Deployment Checklist for Render

## Pre-Deployment

- [ ] Code is committed to Git
- [ ] GitHub repository is created and code is pushed
- [ ] Render account is created (free tier available)
- [ ] Review `render.yaml` configuration

## Backend Deployment

- [ ] Create Web Service on Render
- [ ] Connect GitHub repository
- [ ] Set Root Directory: `unified_tools_backend`
- [ ] Set Build Command: `pip install -r requirements.txt`
- [ ] Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Add environment variables (see `.env.production.example`)
- [ ] Set Health Check Path: `/health`
- [ ] Deploy and verify at `/health` endpoint

## Frontend Deployment

- [ ] Create Web Service on Render
- [ ] Connect GitHub repository
- [ ] Set Root Directory: `blackhole-frontend`
- [ ] Set Build Command: `npm install && npm run build`
- [ ] Set Start Command: `npm start`
- [ ] Add environment variables:
  - [ ] `NEXT_PUBLIC_NOOPUR_API_BASE` = Backend URL
  - [ ] `NEXT_PUBLIC_SANKALP_API_BASE` = Backend URL
  - [ ] `NEXT_PUBLIC_SEEYA_API_BASE` = Backend URL
  - [ ] `NEXT_PUBLIC_ENV` = production
- [ ] Deploy and verify frontend loads

## Post-Deployment

- [ ] Update CORS in `main.py` with frontend URL
- [ ] Test API endpoints from frontend
- [ ] Verify video playback works
- [ ] Test news scraping workflow
- [ ] Monitor logs for errors
- [ ] Set up alerts (optional)

## URLs to Save

- Backend URL: `https://YOUR-BACKEND-NAME.onrender.com`
- Frontend URL: `https://YOUR-FRONTEND-NAME.onrender.com`
- API Docs: `https://YOUR-BACKEND-NAME.onrender.com/docs`
- Health Check: `https://YOUR-BACKEND-NAME.onrender.com/health`

## Common Issues

### Build Fails
- Check Python/Node versions
- Verify all dependencies in requirements.txt/package.json
- Review build logs in Render Dashboard

### Service Won't Start
- Check start command is correct
- Verify environment variables are set
- Review service logs

### CORS Errors
- Add frontend URL to CORS allowed origins in main.py
- Redeploy backend after updating

### Cold Start Delays
- Free tier services sleep after 15 min inactivity
- First request may take 30-60 seconds
- Consider upgrading to paid tier for always-on service

## Need Help?

See `RENDER_DEPLOYMENT.md` for detailed instructions.
