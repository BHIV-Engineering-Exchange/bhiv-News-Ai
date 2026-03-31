# Render Deployment Guide - MongoDB Configuration

## ✓ Fixed: MongoDB Connection on Render

### Problem
```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused
```

**Root Cause**: Backend was trying to connect to `localhost:27017` (local MongoDB) instead of MongoDB Atlas cloud database because `MONGODB_URL` environment variable was not set on Render.

---

## ✓ Solution Applied

### 1. **Database Module Improvements** (database.py)
- ✓ Removed fallback to `localhost:27017`
- ✓ Added validation: MONGODB_URL is **required**
- ✓ Better error messages with setup instructions
- ✓ Connection URL is masked in logs (password hidden)
- ✓ Improved timeout settings: `connectTimeoutMS=10000`
- ✓ Connection pooling: `maxPoolSize=50, minPoolSize=10`
- ✓ Detailed error reporting to stderr for debugging

### 2. **Lazy Database Initialization** (database.py)
- ✓ `init_db()` - Initialize connection at startup
- ✓ `get_db()` - Get database instance (lazy-loaded)
- ✓ `is_db_ready()` - Check if DB is connected
- ✓ Non-blocking: App starts even if DB is unavailable
- ✓ Better error handling and logging

### 3. **App Startup/Shutdown Handlers** (main.py)
- ✓ `@app.on_event("startup")` - Initialize DB at app startup
- ✓ `@app.on_event("shutdown")` - Gracefully close DB connection
- ✓ Logs connection status to stderr for monitoring
- ✓ Handles failures gracefully

### 4. **Enhanced Health Check** (main.py)
- ✓ `/health` endpoint now reports database status
- ✓ Returns `db.connected: true/false`
- ✓ Overall status is `healthy` or `degraded` based on DB
- ✓ Useful for Render health checks and debugging

---

## Deployment Checklist

### Step 1: Set Environment Variables on Render ⚡

Go to Render Dashboard → Your Service → Environment

**Required Variables:**

```
MONGODB_URL=mongodb+srv://blackholeinfiverse59_db_user:blackhole%40059@samachar.mymshbv.mongodb.net/?appName=Samachar
DATABASE_NAME=news_ai_db
```

**Other Required Variables (if not already set):**

```
JWT_SECRET_KEY=<generate-secure-random-string>
ENVIRONMENT=production
PORT=10000
HOST=0.0.0.0
ALLOWED_ORIGINS=https://your-frontend-url.com,https://other-domains.com
```

**Optional Variables:**

```
ENABLE_OPENAI=0
OPENAI_API_KEY=
ENABLE_GROK=0
GROK_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
SERPER_API_KEY=
YOUTUBE_API_KEY=
TWITTER_BEARER_TOKEN=
```

### Step 2: Verify MONGODB_URL Format ✓

Your connection string MUST:
- ✓ Start with `mongodb+srv://` (not `mongodb://`)
- ✓ Include username: `blackholeinfiverse59_db_user`
- ✓ Include URL-encoded password: `blackhole%40059` (NOT `blackhole@059`)
- ✓ Include cluster: `samachar.mymshbv.mongodb.net`
- ✓ Include query params: `?appName=Samachar`

**Correct Format:**
```
mongodb+srv://blackholeinfiverse59_db_user:blackhole%40059@samachar.mymshbv.mongodb.net/?appName=Samachar
```

### Step 3: MongoDB Atlas IP Whitelist ✓

Ensure Render's IP is whitelisted:
1. Go to MongoDB Atlas Dashboard
2. Network Access → IP Whitelist
3. Add IP: `0.0.0.0/0` OR add Render's specific IP
4. Or use: "Allow access from anywhere" (less secure but works for testing)

### Step 4: Verify Build Script

Ensure `render.yaml` or service settings use:
```yaml
buildCommand: pip install -r requirements.txt
startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Or in Render dashboard:
```
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 5: Deploy and Monitor ✓

1. **Deploy** the service on Render
2. **Check logs** in Render dashboard for:
   ```
   ✓ Attempting MongoDB connection...
   ✓ Successfully connected to MongoDB database: news_ai_db
   ✓ MongoDB collections initialized
   ```

3. **Test health endpoint**:
   ```bash
   curl https://your-service.onrender.com/health
   ```

4. **Expected response**:
   ```json
   {
     "status": "healthy",
     "database": {
       "connected": true,
       "type": "mongodb",
       "status": "Ready"
     },
     "services": { ... }
   }
   ```

---

## Debugging Failed Deployments

### Check 1: MONGODB_URL Not Set
**Error**: `ERROR: MONGODB_URL environment variable is not set`

**Fix**: 
1. Go to Render Dashboard
2. Service → Environment
3. Add `MONGODB_URL` variable

### Check 2: Connection Timeout
**Error**: `ServerSelectionTimeoutError: localhost:27017`

**Fix**:
1. Verify MONGODB_URL is set (not using localhost fallback)
2. Check MongoDB Atlas IP whitelist
3. Verify you can ping MongoDB Atlas from your local machine

### Check 3: Authentication Failed
**Error**: `error: 'auth failed'` or `error: 'unauthorized'`

**Fix**:
1. Check username in MONGODB_URL
2. Verify password is URL-encoded (@ → %40)
3. Verify user has access to the database

### Check 4: Database Name Not Found
**Error**: `OperationFailure: namespace does not exist`

**Fix**:
1. Verify `DATABASE_NAME` env var matches MongoDB database
2. Default is `news_ai_db`
3. Collections auto-create on first connection

### Check 5: Connection Refused Locally
**Error**: `Connection refused (configured timeouts:...)`

**Fix**:
1. If testing locally, ensure MongoDB is running OR
2. Set MONGODB_URL to Atlas connection string
3. Don't use `localhost:27017` in production

---

## Monitoring in Production

### Health Check Endpoint
```bash
# Check service health
GET /health

# Expected database status
{
  "status": "healthy|degraded",
  "database": {
    "connected": true|false,
    "type": "mongodb",
    "status": "Ready|Unavailable"
  }
}
```

### Logs to Watch
```
✓ Successfully connected to MongoDB database: news_ai_db
✓ MongoDB collections initialized
✗ MongoDB connection failed: ...
✗ Database initialization failed: ...
```

### Metrics
- Monitor error rate in Render dashboard
- Check 5xx errors (500, 502, 503, 504)
- If 503s spike, database might be down
- Use `/health` endpoint to verify DB status

---

## Files Modified for Render Compatibility

```
unified_tools_backend/
├── database.py
│   ├── Removed localhost fallback
│   ├── Required MONGODB_URL validation
│   ├── Improved error messages
│   ├── Added connection pooling
│   └── Lazy initialization functions
│
├── main.py
│   ├── Added @app.on_event("startup")
│   ├── Added @app.on_event("shutdown")
│   └── Enhanced /health endpoint
│
└── requirements.txt (same - pymongo already included)
```

---

## Environment Variable Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `MONGODB_URL` | YES | `mongodb+srv://...` | Must use URL-encoded password |
| `DATABASE_NAME` | NO | `news_ai_db` | Default: news_ai_db |
| `JWT_SECRET_KEY` | NO | (any random string) | Auto-generated if not set |
| `ENVIRONMENT` | NO | `production` | For logging/debugging |
| `PORT` | NO | `10000` | Render sets automatically |
| `HOST` | NO | `0.0.0.0` | Always use 0.0.0.0 for Render |

---

## Testing Locally First

### 1. Test with Local MongoDB
```bash
# Set env var to local MongoDB
export MONGODB_URL="mongodb://localhost:27017"
export DATABASE_NAME="news_ai_db"

# Start backend
uvicorn main:app --reload

# Test health
curl http://localhost:8000/health
```

### 2. Test with MongoDB Atlas
```bash
# Set env var to MongoDB Atlas
export MONGODB_URL="mongodb+srv://user:password%40@cluster.mongodb.net/?appName=App"

# Start backend
uvicorn main:app --reload

# Test health
curl http://localhost:8000/health
```

---

## Performance Tuning

Current settings in database.py:
```python
MongoClient(
    serverSelectionTimeoutMS=10000,    # 10 second timeout
    connectTimeoutMS=10000,             # 10 second connection timeout
    socketTimeoutMS=10000,              # 10 second socket timeout
    retryWrites=True,                   # Enable retries
    maxPoolSize=50,                     # Max 50 connections
    minPoolSize=10                      # Min 10 connections
)
```

Increase timeouts if experiencing intermittent connection issues:
```python
serverSelectionTimeoutMS=20000  # 20 seconds
connectTimeoutMS=20000
socketTimeoutMS=20000
```

---

## Production Best Practices

1. ✓ Use MongoDB Atlas (not local MongoDB)
2. ✓ IP Whitelist Render's IP addresses
3. ✓ Use strong, complex passwords
4. ✓ URL-encode special characters in passwords
5. ✓ Monitor database connection pool usage
6. ✓ Set up alerts for 5xx errors
7. ✓ Use `/health` endpoint in Render's health check settings
8. ✓ Document all environment variables
9. ✓ Rotate credentials regularly
10. ✓ Backup MongoDB data regularly

---

**Last Updated**: March 31, 2026
**Status**: ✓ Production Ready
**Tested**: ✓ MongoDB Atlas connection verified
