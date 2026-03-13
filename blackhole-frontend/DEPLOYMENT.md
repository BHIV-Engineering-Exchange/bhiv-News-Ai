# 🚀 Deployment Guide - News AI Frontend

Complete guide for deploying the News AI Frontend to production environments.

---

## 📋 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] No linter errors
- [ ] Environment variables configured
- [ ] Backend API accessible
- [ ] Build completed successfully
- [ ] Performance optimized
- [ ] Security review complete

---

## 🌐 Deployment Options

### 1. Vercel (Recommended)

#### Why Vercel?

- Zero configuration deployment
- Automatic HTTPS
- Global CDN
- Serverless functions support
- Preview deployments for PRs

#### Steps:

1. **Install Vercel CLI**

```bash
npm install -g vercel
```

2. **Login to Vercel**

```bash
vercel login
```

3. **Deploy**

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod
```

#### 4. Configure Environment Variables

In Vercel Dashboard:

- Go to Project Settings → Environment Variables
- Add the following variables (Production Values):
  - `NEXT_PUBLIC_NOOPUR_API_BASE` = `https://your-gateway-url.com` (Main Gateway)
  - `NEXT_PUBLIC_SANKALP_API_BASE` = `https://your-tools-url.com` (Legacy Tools)
  - `NEXT_PUBLIC_SEEYA_API_BASE` = `https://your-gateway-url.com` (Orchestration)
  - `NEXT_PUBLIC_AUDIO_BASE_URL` = `https://your-core-url.com/api/audio` (Audio Service)
  - `NEXT_PUBLIC_JWT_TOKEN` = (Your Secure Token)
  - `NEXT_PUBLIC_HMAC_SECRET` = (Your Secure Secret)

#### 5. Custom Domain (Optional)

- Go to Project Settings → Domains
- Add your custom domain
- Update DNS records as instructed

---

### 2. Netlify

#### Steps:

1. **Install Netlify CLI**

```bash
npm install -g netlify-cli
```

2. **Build the project**

```bash
npm run build
```

3. **Deploy**

```bash
netlify deploy --prod
```

4. **Configuration**

Create `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

### 3. Docker Deployment

#### Dockerfile

Create `Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy necessary files from builder
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    image: your-backend-image:latest
    ports:
      - "8000:8000"
    restart: unless-stopped
```

#### Deploy:

```bash
# Build image
docker build -t news-ai-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://your-backend-url \
  news-ai-frontend

# Or use docker-compose
docker-compose up -d
```

---

### 4. AWS Deployment

#### Option A: AWS Amplify

1. **Connect Repository**

- Go to AWS Amplify Console
- Connect your GitHub repository
- Configure build settings

2. **Build Settings**

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

#### Option B: AWS EC2

1. **Launch EC2 Instance**

- Choose Ubuntu 22.04 LTS
- t3.small or larger
- Configure security groups (allow ports 80, 443, 22)

2. **SSH into Instance**

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2
```

4. **Deploy Application**

```bash
# Clone repository
git clone your-repo-url
cd blackhole-frontend

# Install dependencies
npm ci

# Build
npm run build

# Start with PM2
pm2 start npm --name "news-ai-frontend" -- start
pm2 save
pm2 startup
```

5. **Setup Nginx Reverse Proxy**

```bash
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/news-ai
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/news-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

6. **SSL with Let's Encrypt**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

### 5. Google Cloud Platform

#### Cloud Run Deployment

1. **Install gcloud CLI**

```bash
# Follow instructions at https://cloud.google.com/sdk/docs/install
```

2. **Build and Deploy**

```bash
# Set project
gcloud config set project your-project-id

# Build image
gcloud builds submit --tag gcr.io/your-project-id/news-ai-frontend

# Deploy to Cloud Run
gcloud run deploy news-ai-frontend \
  --image gcr.io/your-project-id/news-ai-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_BASE_URL=your-backend-url
```

---

### 6. Azure Deployment

#### Azure Static Web Apps

1. **Install Azure CLI**

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

2. **Login**

```bash
az login
```

3. **Deploy**

```bash
az staticwebapp create \
  --name news-ai-frontend \
  --resource-group your-resource-group \
  --location "East US 2" \
  --source https://github.com/your-repo \
  --branch main \
  --app-location "/" \
  --output-location ".next"
```

---

## 🔒 Security Considerations

### Environment Variables

**Never commit sensitive data!**

Create `.env.production`:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
# Add other non-sensitive public variables
```

For sensitive server-side variables, use your hosting provider's environment variable management.

### CORS Configuration

Ensure backend allows your frontend domain:

```python
# Python backend example
ALLOWED_ORIGINS = [
    "https://your-domain.com",
    "https://www.your-domain.com"
]
```

### HTTPS

Always use HTTPS in production:

- Vercel/Netlify: Automatic
- Custom server: Use Let's Encrypt or your provider's SSL

---

## 📊 Performance Optimization

### 1. Image Optimization

Use Next.js Image component:

```tsx
import Image from 'next/image'

<Image
  src="/path/to/image.jpg"
  width={800}
  height={600}
  alt="Description"
  loading="lazy"
/>
```

### 2. Code Splitting

Next.js handles this automatically, but you can optimize further:

```tsx
import dynamic from 'next/dynamic'

const DynamicComponent = dynamic(() => import('./Component'), {
  loading: () => <p>Loading...</p>,
  ssr: false
})
```

### 3. Caching

Configure caching in `next.config.js`:

```javascript
module.exports = {
  async headers() {
    return [
      {
        source: '/:all*(svg|jpg|png|webp)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
}
```

---

## 🔍 Monitoring

### 1. Error Tracking (Sentry)

```bash
npm install @sentry/nextjs
```

`sentry.config.js`:

```javascript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
});
```

### 2. Analytics (Google Analytics)

Add to `app/layout.tsx`:

```tsx
import Script from 'next/script'

<Script
  src={`https://www.googletagmanager.com/gtag/js?id=${GA_TRACKING_ID}`}
  strategy="afterInteractive"
/>
```

### 3. Performance Monitoring

Use Vercel Analytics or Lighthouse CI:

```bash
npm install -D @vercel/analytics
```

---

## 🧪 Testing Before Deployment

### 1. Run Production Build Locally

```bash
npm run build
npm start
```

Test on http://localhost:3000

### 2. Lighthouse Audit

```bash
npm install -g lighthouse

lighthouse http://localhost:3000 --view
```

### 3. Load Testing

```bash
npm install -g artillery

artillery quick --count 10 --num 100 http://localhost:3000
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
  
    steps:
      - uses: actions/checkout@v2
  
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
    
      - name: Run tests
        run: npm test
    
      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_API_BASE_URL: ${{ secrets.API_BASE_URL }}
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

## 📝 Post-Deployment Checklist

- [ ] Application accessible at production URL
- [ ] All pages loading correctly
- [ ] API integration working
- [ ] TTS audio playback functional
- [ ] Feedback system operational
- [ ] SSL certificate valid
- [ ] DNS records updated
- [ ] Analytics tracking active
- [ ] Error monitoring configured
- [ ] Performance metrics within targets
- [ ] Mobile responsiveness verified
- [ ] Cross-browser testing completed

---

## 🐛 Troubleshooting

### Build Failures

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### Runtime Errors

Check logs:

- Vercel: View deployment logs in dashboard
- Docker: `docker logs container-name`
- PM2: `pm2 logs news-ai-frontend`

### API Connection Issues

- Verify CORS settings
- Check environment variables
- Test API endpoint directly
- Review network security groups

---

## 📞 Support

For deployment issues:

1. Check documentation
2. Review error logs
3. Contact DevOps team
4. Create support ticket

---

**Deployment guide last updated: November 2024**
