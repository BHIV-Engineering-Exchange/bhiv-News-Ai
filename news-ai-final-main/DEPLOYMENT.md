# Noopur News AI - Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] All environment variables configured
- [ ] MongoDB Atlas production cluster setup
- [ ] Uniguru API credentials validated
- [ ] BHIV endpoints configured
- [ ] SSL/TLS certificates ready
- [ ] Load balancer configured
- [ ] Monitoring/alerting setup
- [ ] Backup strategy in place

---

## Deployment Platforms

### Option 1: Heroku Deployment

```bash
# 1. Install Heroku CLI
npm install -g heroku

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create noopur-news-ai

# 4. Set environment variables
heroku config:set MONGODB_URI=mongodb+srv://...
heroku config:set UNIGURU_API_KEY=...
heroku config:set BHIV_API_URL=...
heroku config:set BHIV_API_KEY=...
heroku config:set LOG_LEVEL=info
heroku config:set NODE_ENV=production

# 5. Deploy
git push heroku main

# 6. View logs
heroku logs --tail

# 7. Scale dynos if needed
heroku ps:scale web=2 worker=1
```

### Option 2: Docker Containerization

**Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY src ./src
COPY config ./config

ENV NODE_ENV=production
EXPOSE 3000 3001

CMD ["npm", "start"]
```

**Build & Run:**
```bash
# Build image
docker build -t noopur-news-ai:1.0 .

# Run container
docker run -d \
  --name noopur-api \
  -p 3000:3000 \
  -p 3001:3001 \
  -e MONGODB_URI="mongodb+srv://..." \
  -e UNIGURU_API_KEY="..." \
  -e BHIV_API_URL="..." \
  -e BHIV_API_KEY="..." \
  noopur-news-ai:1.0

# View logs
docker logs -f noopur-api
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
      - "3001:3001"
    environment:
      NODE_ENV: production
      MONGODB_URI: ${MONGODB_URI}
      UNIGURU_API_KEY: ${UNIGURU_API_KEY}
      BHIV_API_URL: ${BHIV_API_URL}
      BHIV_API_KEY: ${BHIV_API_KEY}
      LOG_LEVEL: info
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  logs:
    driver: local
```

Run with: `docker-compose up -d`

### Option 3: AWS Deployment

**Using AWS Lambda + API Gateway:**

```bash
# 1. Install serverless framework
npm install -g serverless

# 2. Create serverless config
# serverless.yml structure for API Gateway + Lambda

# 3. Deploy
serverless deploy --region us-east-1
```

**Using AWS EC2:**

```bash
# 1. SSH into EC2 instance
ssh -i key.pem ec2-user@instance-ip

# 2. Install Node & npm
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 3. Clone repository
git clone <repo> /home/ec2-user/noopur-news-ai
cd /home/ec2-user/noopur-news-ai

# 4. Install dependencies
npm install

# 5. Setup PM2
sudo npm install -g pm2
pm2 start src/index.js --name "noopur-api"
pm2 save
pm2 startup

# 6. Setup Nginx reverse proxy
sudo yum install -y nginx
# Configure nginx.conf to proxy to localhost:3000
```

### Option 4: Google Cloud Run

```bash
# 1. Authenticate with GCP
gcloud auth login
gcloud config set project noopur-news-ai

# 2. Build container image
gcloud builds submit --tag gcr.io/noopur-news-ai/api

# 3. Deploy to Cloud Run
gcloud run deploy noopur-api \
  --image gcr.io/noopur-news-ai/api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URI=mongodb+srv://...

# 4. View service
gcloud run services list
```

---

## Process Management with PM2

**ecosystem.config.js:**
```javascript
module.exports = {
  apps: [
    {
      name: "noopur-api",
      script: "./src/index.js",
      instances: 2,
      exec_mode: "cluster",
      env: {
        NODE_ENV: "production",
        PORT: 3000,
        WS_PORT: 3001
      },
      error_file: "./logs/error.log",
      out_file: "./logs/out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      merge_logs: true,
      max_memory_restart: "500M"
    }
  ]
};
```

**Commands:**
```bash
# Start
pm2 start ecosystem.config.js

# Restart
pm2 restart noopur-api

# Stop
pm2 stop noopur-api

# View logs
pm2 logs noopur-api

# Monitor
pm2 monit

# Setup auto-restart on reboot
pm2 save
pm2 startup
```

---

## Nginx Reverse Proxy Configuration

**File: `/etc/nginx/sites-available/noopur-news-ai`**

```nginx
upstream api_backend {
    server localhost:3000;
    server localhost:3000;  # If running multiple instances
}

upstream ws_backend {
    server localhost:3001;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.noopur.news;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name api.noopur.news;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.noopur.news/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.noopur.news/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # REST API
    location /api/ {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 30s;
    }

    # Health check
    location /health {
        proxy_pass http://api_backend;
    }

    # WebSocket
    location / {
        # Check for WebSocket upgrade
        if ($http_upgrade = "websocket") {
            proxy_pass http://ws_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            break;
        }
        
        proxy_pass http://api_backend;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/noopur-news-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL Certificate Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d api.noopur.news

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Verify auto-renewal
sudo certbot renew --dry-run
```

---

## Monitoring & Logging

### CloudWatch (AWS)

```javascript
// In src/index.js
import CloudWatchTransport from 'winston-cloudwatch';

logger.add(new CloudWatchTransport({
  logGroupName: '/aws/lambda/noopur-news-ai',
  logStreamName: 'production',
  awsRegion: 'us-east-1',
  messageFormatter: ({ level, message, meta }) => 
    `[${level}] ${message} ${JSON.stringify(meta)}`
}));
```

### DataDog

```javascript
// In src/index.js
import StatsD from 'node-statsd';

const statsd = new StatsD();

// Track metrics
statsd.gauge('news.processing_time', processingTime);
statsd.increment('news.published');
statsd.histogram('reward.score', rewardScore);
```

### New Relic

```javascript
// Add to top of src/index.js
require('newrelic');

// Then use built-in instrumentation for database, API calls, etc.
```

---

## Database Optimization for Production

### MongoDB Atlas Settings

```javascript
// Connection string with optimization parameters
const uri = `mongodb+srv://user:pass@cluster.mongodb.net/noopur_news?
  retryWrites=true&
  w=majority&
  maxPoolSize=20&
  minPoolSize=5&
  maxIdleTimeMS=30000&
  connectTimeoutMS=10000&
  socketTimeoutMS=45000`;

// Connection options
const options = {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  maxPoolSize: 20,
  socketTimeoutMS: 45000,
  serverSelectionTimeoutMS: 5000
};
```

### Index Optimization

```javascript
// In src/models/schemas.js
newsItemSchema.index({ status: 1, createdAt: -1 });
newsItemSchema.index({ 'classification.category': 1 });
newsItemSchema.index({ 'sentiment.label': 1 });
newsItemSchema.index({ 'verification.verified': 1 });
newsItemSchema.index({ updatedAt: -1 });

// Agent task indexes
agentTaskSchema.index({ agentId: 1, status: 1 });
agentTaskSchema.index({ status: 1, createdAt: -1 });
agentTaskSchema.index({ newsItemId: 1 });
agentTaskSchema.index({ completedAt: -1 });
```

### TTL Index for Auto-Cleanup

```javascript
// Auto-delete old raw items after 90 days
newsItemSchema.index(
  { createdAt: 1 },
  { 
    expireAfterSeconds: 7776000,  // 90 days
    partialFilterExpression: { status: 'raw' }
  }
);
```

---

## Health Checks & Monitoring

### Application Health Endpoint

```javascript
app.get('/health', (req, res) => {
  const checks = {
    database: dbConnected ? 'ok' : 'down',
    uniguru: uniguruHealthy ? 'ok' : 'down',
    memory: process.memoryUsage().heapUsedPercent < 90 ? 'ok' : 'warning',
    uptime: process.uptime()
  };
  
  const allHealthy = Object.values(checks).every(v => v === 'ok');
  res.status(allHealthy ? 200 : 503).json(checks);
});
```

### Load Balancer Health Check

```bash
# Configure health check on load balancer:
# - Endpoint: /health
# - Interval: 30 seconds
# - Timeout: 5 seconds
# - Healthy threshold: 2 consecutive successes
# - Unhealthy threshold: 3 consecutive failures
```

---

## Backup & Recovery

### MongoDB Backup Strategy

```bash
# Automated daily backup via MongoDB Atlas
# Settings → Backup & Restore → Enable Backup

# Manual backup
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/noopur_news" \
  --out=/backups/noopur-$(date +%Y%m%d)

# Restore from backup
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net" \
  /backups/noopur-20240101
```

### Application Backup

```bash
# Git-based version control
git tag production-v1.0
git tag production-v2.0

# Full server snapshot
aws ec2 create-image --instance-id i-1234567890abcdef0 \
  --name noopur-api-snapshot-$(date +%Y%m%d)
```

---

## Performance Tuning

### Node.js Optimization

```bash
# Set cluster mode
NODE_CLUSTER_SCHED_POLICY=rr  # Round-robin scheduling

# Increase file descriptors
ulimit -n 65536

# Enable clustering (see PM2 config above)
# Run 1-2 instances per CPU core
```

### Database Query Optimization

```javascript
// Use projections to fetch only needed fields
NewsItem.find({ status: 'raw' }, { title: 1, _id: 1 });

// Use batch operations
await NewsItem.insertMany(items, { ordered: false });

// Limit result sets
NewsItem.find({}).limit(1000).lean();
```

### Caching Strategy

```javascript
// Redis caching (optional)
import redis from 'redis';

const client = redis.createClient({
  url: process.env.REDIS_URL
});

// Cache Uniguru responses
const cachedResult = await client.get(`uniguru:${title}`);
if (!cachedResult) {
  const result = await uniguruService.classify(title, content);
  await client.setEx(`uniguru:${title}`, 3600, JSON.stringify(result));
}
```

---

## Security Hardening

### Input Validation

```javascript
// Validate all inputs
const schema = Joi.object({
  title: Joi.string().max(500).required(),
  content: Joi.string().max(10000).required(),
  source: Joi.string().valid('rss', 'api', 'manual', 'social').required()
});

const { value, error } = schema.validate(req.body);
if (error) return res.status(400).json({ error: error.details });
```

### Rate Limiting

```javascript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,  // 100 requests per window
  message: 'Too many requests, please try again later'
});

app.use('/api/news', limiter);
```

### CORS Configuration

```javascript
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  methods: ['GET', 'POST', 'PUT'],
  credentials: true
}));
```

### API Key Authentication

```javascript
const validateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey || !validApiKeys.includes(apiKey)) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  
  next();
};

app.use('/api/bhiv', validateApiKey);
```

---

## Rollback Plan

### Blue-Green Deployment

```bash
# Blue environment (current)
# Green environment (new)

# 1. Deploy to green
npm run build
npm test

# 2. Route traffic to green
# Update load balancer target group

# 3. Monitor green for errors
# If critical error detected, switch back to blue
```

### Version Tagging

```bash
# Tag each production release
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0

# Rollback procedure
git checkout v0.9.9
npm install
npm start
```

---

## Documentation & Runbooks

Create incident response documentation:

```markdown
# Incident Runbook

## High Error Rate
1. Check logs: `pm2 logs noopur-api`
2. Check database: MongoDB Atlas dashboard
3. Check Uniguru API status
4. Restart if needed: `pm2 restart noopur-api`

## Database Connection Issues
1. Verify connection string
2. Check IP whitelist
3. Restart connection pool

## WebSocket Disconnections
1. Restart WebSocket server
2. Check network connectivity
3. Verify port availability
```

---

## Cost Optimization

### MongoDB Atlas
- Use shared cluster for development
- Use M10+ instances for production
- Enable auto-scaling
- Set appropriate backup retention

### Compute Resources
- Use spot instances for non-critical workloads
- Auto-scale based on CPU/memory metrics
- Monitor and optimize code
- Use caching to reduce API calls

---

*Last Updated: November 2024*
