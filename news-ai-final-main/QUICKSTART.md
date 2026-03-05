# Noopur News AI - Quick Start Guide

## 🚀 Getting Started (5 Minutes)

### Prerequisites
- Node.js 18+ 
- MongoDB Atlas account (free tier works)
- Uniguru API key (or skip for mock mode)
- npm or yarn

### Step 1: Clone & Setup

```bash
cd "c:\Users\black\Downloads\Noopur News ai"
npm install
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
```

**Required:**
```
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/noopur_news
UNIGURU_API_KEY=your_api_key_here (optional for demo)
BHIV_API_URL=http://localhost:8000 (or production URL)
BHIV_API_KEY=your_bhiv_key_here
```

### Step 3: Initialize Database

```bash
npm run seed-db
```

### Step 4: Start Server

```bash
# Production
npm start

# Development with auto-reload
npm run dev
```

Expected output:
```
🚀 Initializing Noopur News AI System...

1️⃣  Connecting to MongoDB Atlas...
✓ MongoDB Atlas connected successfully

2️⃣  Initializing Uniguru Service...
3️⃣  Initializing Agent Registry...
✓ Agent registered: agent-fetch-xyz (fetch)
✓ Agent registered: agent-filter-abc (filter)
✓ Agent registered: agent-verify-def (verify)
✓ Agent registered: agent-script-ghi (script)
✓ Agent registered: agent-rlfeedback-jkl (rlfeedback)

4️⃣  Initializing RL Feedback Loop...
5️⃣  Initializing LangGraph Pipeline...
6️⃣  Setting up API routes...

✓ Express server running on http://localhost:3000
✓ WebSocket server running on ws://localhost:3001

✅ Noopur News AI System Ready!
```

### Step 5: Test with Sample News

```bash
# In another terminal

# 1. Create a news item
curl -X POST http://localhost:3000/api/news \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Breaking: AI Breakthrough Announced",
    "content": "Researchers have announced a major breakthrough in artificial intelligence, achieving human-level reasoning across complex tasks...",
    "source": "api",
    "sourceUrl": "https://example.com/news"
  }'

# Response:
# {
#   "success": true,
#   "message": "News item created and enrichment started",
#   "newsId": "507f1f77bcf86cd799439011",
#   "status": "raw"
# }

# 2. Check status (wait a few seconds for enrichment)
curl http://localhost:3000/api/news/507f1f77bcf86cd799439011

# 3. Process through pipeline
curl -X POST http://localhost:3000/api/bhiv/process \
  -H "Content-Type: application/json" \
  -d '{
    "newsItemId": "507f1f77bcf86cd799439011",
    "distribution": {"ttv": true, "vaani": true}
  }'

# 4. Check system status
curl http://localhost:3000/api/system/info

# 5. Health check
curl http://localhost:3000/health
```

## 📊 Sample News Validation

Test with 5 pre-loaded sample news items:

```bash
npm run validate-samples
```

This will:
- Create 5 sample news items (Technology, Climate, Finance, Sports, Medical)
- Demonstrate Uniguru enrichment
- Show pipeline processing
- Display validation report

## 🌐 WebSocket Connection

Monitor real-time updates:

```bash
# Using websocat (install if needed)
websocat ws://localhost:3001

# Then send messages like:
{"type": "subscribe", "newsItemId": "507f1f77bcf86cd799439011"}
{"type": "request_stats"}
{"type": "request_agents"}
```

Or use a WebSocket client:

```javascript
const ws = new WebSocket('ws://localhost:3001');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    newsItemId: '507f1f77bcf86cd799439011'
  }));
};

ws.onmessage = (event) => {
  console.log('Update:', JSON.parse(event.data));
};
```

## 📈 Key Endpoints to Try

### News Management
```bash
# Get all published news
curl http://localhost:3000/api/news/status/published

# Get all verified news  
curl http://localhost:3000/api/news/status/verified

# Get specific news item
curl http://localhost:3000/api/news/{newsId}
```

### System Status
```bash
# System info & agents
curl http://localhost:3000/api/system/info

# Health check
curl http://localhost:3000/health
```

### BHIV Integration
```bash
# Process single news item
curl -X POST http://localhost:3000/api/bhiv/process \
  -H "Content-Type: application/json" \
  -d '{"newsItemId": "{newsId}", "distribution": {"ttv": true, "vaani": true}}'

# Stream to BHIV
curl -X POST http://localhost:3000/api/bhiv/stream \
  -H "Content-Type: application/json" \
  -d '{"target": "ttv", "filter": {"status": "published"}}'

# Check distribution status
curl http://localhost:3000/api/bhiv/status/{newsId}
```

## 🔧 Troubleshooting

### MongoDB Connection Failed
```
Error: MongoDB connection error

Solution:
1. Check MONGODB_URI in .env
2. Ensure MongoDB Atlas IP whitelist includes your IP
3. Verify credentials are correct
4. Check internet connection
```

### Uniguru API Key Invalid
```
Error: Uniguru API error

Solution:
1. Verify API key in .env
2. Check Uniguru API status
3. Can work in demo mode without API key (uses mock responses)
```

### Port Already in Use
```
Error: EADDRINUSE :::3000

Solution:
# Find process using port 3000
netstat -ano | findstr :3000

# Kill it (Windows)
taskkill /PID {PID} /F

# Or change PORT in .env
PORT=3001
```

### WebSocket Connection Refused
```
Error: WebSocket connection error

Solution:
1. Ensure main server is running (npm run dev)
2. Check WS_PORT in .env (default 3001)
3. Try connecting to correct address: ws://localhost:3001
```

## 📚 Project Structure

```
noopur-news-ai/
├── src/
│   ├── index.js                 # Main server file
│   ├── db/
│   │   ├── connection.js        # MongoDB operations
│   │   └── seed.js              # Database seeding
│   ├── models/
│   │   └── schemas.js           # Mongoose schemas
│   ├── services/
│   │   └── uniguru.js           # Uniguru API wrapper
│   ├── agents/
│   │   ├── registry.js          # Agent Registry class
│   │   └── initialize.js        # Agent initialization
│   ├── feedback/
│   │   └── rl_loop.js           # RL Feedback Loop
│   ├── pipeline/
│   │   └── langgraph.js         # LangGraph automation
│   ├── routes/
│   │   ├── news.js              # News API routes
│   │   └── bhiv.js              # BHIV integration routes
│   └── validation/
│       └── validate-samples.js  # Sample validation
├── config/
├── tests/
├── logs/                        # Application logs
├── .env.example                 # Environment template
├── package.json                 # Dependencies
├── README.md                    # Project overview
├── API_DOCUMENTATION.md         # Complete API reference
└── ARCHITECTURE.md              # System architecture
```

## 🎯 Next Steps

1. **Integrate with BHIV**
   - Update `.env` with BHIV API URL and key
   - Test BHIV endpoints

2. **Customize Agents**
   - Modify agent handlers in `src/agents/initialize.js`
   - Adjust thresholds and timeouts

3. **Tune RL Feedback**
   - Adjust reward thresholds
   - Add custom evaluation metrics
   - Modify correction type detection

4. **Production Deployment**
   - Set up PM2 for process management
   - Configure logging to files
   - Enable CORS and rate limiting
   - Use environment-specific configs

## 📖 Documentation

- **[API Documentation](./API_DOCUMENTATION.md)** - Complete endpoint reference
- **[Architecture Guide](./ARCHITECTURE.md)** - System design & components
- **[README.md](./README.md)** - Project overview

## 🆘 Support

### Logging
Logs are written to:
- Console (development)
- `logs/uniguru.log` (Uniguru service)
- MongoDB (processing history)

Set log level in `.env`:
```
LOG_LEVEL=debug    # More verbose
LOG_LEVEL=info     # Normal
LOG_LEVEL=error    # Only errors
```

### Database Inspection

View data with MongoDB Compass or Atlas UI:
- `news_items` - Raw → verified → published pipeline
- `agent_tasks` - Task execution history
- `feedback_metrics` - RL reward and correction data

### Performance Monitoring

Check system info endpoint:
```bash
curl http://localhost:3000/api/system/info | jq
```

Monitor WebSocket for real-time metrics:
```bash
websocat ws://localhost:3001
{"type": "request_stats"}
{"type": "request_agents"}
```

---

**Happy News Processing! 🚀**

For more details, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) and [ARCHITECTURE.md](./ARCHITECTURE.md)
