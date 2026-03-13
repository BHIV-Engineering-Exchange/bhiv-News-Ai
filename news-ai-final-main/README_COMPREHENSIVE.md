# 📰 Noopur News AI - Advanced News Processing System

![Status](https://img.shields.io/badge/status-production--ready-green)
![Node.js](https://img.shields.io/badge/Node.js-18+-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)
![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-blue)

> An intelligent microservice backend for news processing featuring AI enrichment, agent-based orchestration, reinforcement learning feedback loops, and automated publishing pipelines.

## 🎯 Project Overview

Noopur News AI is a comprehensive system designed to process news items through multiple stages of intelligent analysis and quality control:

```
Raw News → Enrichment → Verification → Scripting → Quality Evaluation → Publishing
  ↓
[Uniguru API for Classification, Sentiment, Summarization]
  ↓
[Agent Registry for Task Orchestration]
  ↓
[RL Feedback Loop for Adaptive Quality]
  ↓
[LangGraph Pipeline for Automation]
  ↓
[BHIV Integration for Distribution]
```

## ✨ Key Features

### 📊 News Pipeline
- **Raw News Ingestion**: Accept news from multiple sources (RSS, API, manual, social)
- **Uniguru Enrichment**: Automatic classification, sentiment analysis, and summarization
- **Status Tracking**: Raw → Verified → Published workflow
- **Processing Logs**: Complete audit trail of each news item's journey

### 🤖 Agent Registry (MCP Core)
- **5 Specialized Agents**:
  - `Fetch Agent` (Priority 10): Validate and retrieve news data
  - `Filter Agent` (Priority 8): Duplicate detection and relevance scoring
  - `Verify Agent` (Priority 9): Fact-checking and credibility assessment
  - `Script Agent` (Priority 7): Narrative generation and scripting
  - `RLFeedback Agent` (Priority 6): Quality evaluation and feedback

- **Task Management**:
  - Async queue-based task routing
  - Priority-based execution (0-10 scale)
  - Automatic retry with exponential backoff (up to 3 retries)
  - 30-second task timeout with configurable limits
  - Real-time queue monitoring

### 💡 RL Feedback Loop
- **Intelligent Reward Calculation**:
  - Tone Accuracy Score (40% weight)
  - Engagement Prediction (60% weight)
  - Composite reward: 0.0 - 1.0 scale
  
- **Adaptive Quality Control**:
  - Auto-reroute items with reward < 0.6
  - Automatic re-analysis with Uniguru
  - Iterative improvement with history tracking
  - Metrics logging: reward, corrections, latency

### 🔄 LangGraph Pipeline
- **Automated Workflow**: Fetch → Verify → Script → Feedback → Publish
- **Self-Correcting**: Up to 3 iterations per item
- **Adaptive Processing**: Intelligent retry on low scores
- **Statistics**: Success rate, avg reward, processing time
- **Batch Processing**: Parallel processing of multiple items

### 🌐 BHIV Integration
- **Multi-Channel Distribution**:
  - **TTV (Text-to-Visual)**: Headlines and visual narratives
  - **Vaani (Voice/Audio)**: Key points and audio narratives
  
- **Streaming**: Batch and single-item publishing
- **Webhooks**: Receive engagement metrics and status updates
- **Real-time Updates**: WebSocket broadcasts of distribution status

### 📡 Real-time Monitoring
- **WebSocket Server** (Port 3001):
  - Live news publication events
  - Stream initiation notifications
  - BHIV status updates
  - System metrics streaming
  
- **REST API**: Comprehensive endpoints for all operations
- **Health Checks**: System status and component health

## 🚀 Quick Start

### Prerequisites
```bash
Node.js 18+
MongoDB Atlas (free tier works)
npm or yarn
```

### Installation

```bash
# Clone repository
cd "Noopur News ai"

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
npm run seed-db

# Start server
npm run dev
```

### First Steps

```bash
# Create a news item
curl -X POST http://localhost:3000/api/news \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Breaking News",
    "content": "News content...",
    "source": "api"
  }'

# View all systems
curl http://localhost:3000/api/system/info

# Monitor in real-time
websocat ws://localhost:3001
{"type": "request_stats"}
```

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - 5-minute setup guide with examples
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete endpoint reference
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and component details
- **[TEST_SCENARIOS.md](./TEST_SCENARIOS.md)** - Test workflows and validation
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guides

## 📁 Project Structure

```
noopur-news-ai/
├── src/
│   ├── index.js                    # Main server entry point
│   ├── db/
│   │   ├── connection.js           # MongoDB operations
│   │   └── seed.js                 # Database initialization
│   ├── models/
│   │   └── schemas.js              # Mongoose schemas
│   ├── services/
│   │   └── uniguru.js              # Uniguru API integration
│   ├── agents/
│   │   ├── registry.js             # Agent Registry class
│   │   └── initialize.js           # Agent initialization
│   ├── feedback/
│   │   └── rl_loop.js              # RL Feedback Loop
│   ├── pipeline/
│   │   └── langgraph.js            # LangGraph automation
│   ├── routes/
│   │   ├── news.js                 # News API endpoints
│   │   └── bhiv.js                 # BHIV integration endpoints
│   └── validation/
│       └── validate-samples.js     # Sample news validation
├── config/                         # Configuration files
├── logs/                           # Application logs
├── tests/                          # Test suite
├── .env.example                    # Environment template
├── package.json                    # Dependencies
├── README.md                       # This file
├── QUICKSTART.md                   # Quick setup guide
├── API_DOCUMENTATION.md            # API reference
├── ARCHITECTURE.md                 # System architecture
├── TEST_SCENARIOS.md               # Test workflows
└── DEPLOYMENT.md                   # Deployment guides
```

## 🔧 Configuration

Create `.env` file:

```env
# MongoDB
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/noopur_news

# Uniguru API
UNIGURU_API_KEY=your_api_key_here
UNIGURU_BASE_URL=https://api.uniguru.com/v1

# BHIV Integration
BHIV_API_URL=http://localhost:8000
BHIV_API_KEY=your_bhiv_api_key_here

# Server
PORT=3000
WS_PORT=3001
NODE_ENV=development

# Logging
LOG_LEVEL=debug
```

## 📊 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/news` | Create raw news item |
| GET | `/api/news/:id` | Get news by ID |
| GET | `/api/news/status/:status` | Get news by status |
| PUT | `/api/news/:id` | Update news item |
| POST | `/api/bhiv/process` | Process through pipeline |
| POST | `/api/bhiv/stream` | Stream to BHIV endpoints |
| POST | `/api/bhiv/webhook` | Receive BHIV feedback |
| GET | `/api/bhiv/status/:id` | Check distribution status |
| GET | `/api/system/info` | System status |
| GET | `/health` | Health check |
| WS | `ws://localhost:3001` | WebSocket events |

## 🧪 Testing

### Sample Validation
```bash
npm run validate-samples
```
Processes 5 pre-loaded news items through the complete pipeline.

### Performance Testing
```bash
bash TEST_SCENARIOS.md  # See file for detailed test scenarios
```

### Load Testing
```bash
# Process 100+ items with metrics collection
./load_test.sh  # Example script in TEST_SCENARIOS.md
```

## 📈 Monitoring & Metrics

### Pipeline Statistics
```bash
curl http://localhost:3000/api/system/info | jq '.pipeline'

# Output:
{
  "totalProcessed": 10,
  "successful": 9,
  "failed": 1,
  "averageRewardScore": 0.84,
  "averageIterations": 1.2,
  "averageProcessingTime": 4200,
  "successRate": "90.00%"
}
```

### Real-time WebSocket Monitoring
```bash
websocat ws://localhost:3001
{"type": "request_stats"}      # Get pipeline stats
{"type": "request_agents"}     # Get agent queue status
{"type": "subscribe", "newsItemId": "xxx"}  # Subscribe to item updates
```

## 🚀 Deployment

### Docker
```bash
docker build -t noopur-news-ai:1.0 .
docker run -p 3000:3000 -p 3001:3001 --env-file .env noopur-news-ai:1.0
```

### PM2 Cluster Mode
```bash
pm2 start ecosystem.config.js
pm2 restart noopur-api
pm2 logs noopur-api
```

### Cloud Deployment
- **Heroku**: `git push heroku main`
- **AWS**: Lambda, EC2, or ECS
- **Google Cloud**: Cloud Run
- **Azure**: App Service

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guides.

## 🔐 Security Features

- ✅ Environment variable-based secrets
- ✅ API key authentication for BHIV
- ✅ Input validation and sanitization
- ✅ Rate limiting support (configurable)
- ✅ CORS configuration
- ✅ SSL/TLS ready
- ✅ Complete audit logging

## 📊 Database Schema

### news_items Collection
```javascript
{
  _id: ObjectId,
  title: String,
  content: String,
  status: 'raw' | 'verified' | 'published',
  source: String,
  classification: {
    category: String,
    subcategory: String,
    confidence: Number
  },
  sentiment: {
    label: 'positive' | 'negative' | 'neutral',
    score: Number,
    aspects: [{aspect, sentiment, score}]
  },
  summary: {
    short: String,
    medium: String,
    keyPoints: [String],
    entities: [{type, value}]
  },
  verification: {
    verified: Boolean,
    verificationScore: Number,
    verificationNotes: String
  },
  feedback: {
    rewardScore: Number,
    toneAccuracy: Number,
    engagementPrediction: Number,
    history: [{iteration, score, timestamp}]
  },
  publishedMetadata: {
    publishedAt: Date,
    distribution: {ttv: Boolean, vaani: Boolean}
  },
  processingLog: [{stage, agent, status, timestamp}],
  createdAt: Date,
  updatedAt: Date
}
```

## 🎯 Use Cases

1. **News Agencies**: Automated news processing and distribution
2. **Content Platforms**: Multi-channel publishing with quality control
3. **Media Monitoring**: Automated content analysis and routing
4. **Information Systems**: Intelligent news aggregation
5. **Research**: News processing pipeline research

## 🔄 Data Flow Example

```
1. News arrives: "AI Breakthrough Announced"
   ↓
2. Create raw news item
   ↓
3. [Async] Uniguru enrichment starts:
   - Classification: Technology > AI
   - Sentiment: Positive (0.82)
   - Summary: Generated short & medium summaries
   ↓
4. News auto-promoted to 'verified'
   ↓
5. User requests processing:
   POST /api/bhiv/process
   ↓
6. Pipeline executes:
   - Fetch Agent: Validate data ✓
   - Verify Agent: Confirm facts ✓
   - Script Agent: Generate narrative ✓
   ↓
7. RL Feedback evaluation:
   - Reward = (Tone × 0.4) + (Engagement × 0.6) = 0.82
   - Score ≥ 0.6? YES → Proceed
   ↓
8. Publish to BHIV:
   - TTV: Text-to-Visual narrative
   - Vaani: Voice/audio version
   ↓
9. Final status: 'published'
   ↓
10. WebSocket broadcast: news_published event
```

## 🎓 Learning Resources

- See [QUICKSTART.md](./QUICKSTART.md) for hands-on examples
- See [TEST_SCENARIOS.md](./TEST_SCENARIOS.md) for workflows
- See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for endpoint details
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design

## 📝 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| MONGODB_URI | Yes | - | MongoDB Atlas connection string |
| UNIGURU_API_KEY | No | - | Uniguru API key |
| UNIGURU_BASE_URL | No | https://api.uniguru.com/v1 | Uniguru API URL |
| BHIV_API_URL | Yes | http://localhost:8000 | BHIV Core API URL |
| BHIV_API_KEY | Yes | - | BHIV API key |
| PORT | No | 3000 | REST API port |
| WS_PORT | No | 3001 | WebSocket port |
| NODE_ENV | No | development | Environment |
| LOG_LEVEL | No | info | Logging level |

## 🐛 Troubleshooting

### MongoDB Connection Issues
- Verify connection string format
- Check IP whitelist in MongoDB Atlas
- Ensure credentials are correct

### Uniguru API Errors
- Verify API key is active
- Check API rate limits
- System works in demo mode without key

### WebSocket Connection Fails
- Ensure WS_PORT is not in use
- Check firewall settings
- Verify browser supports WebSocket

See [DEPLOYMENT.md](./DEPLOYMENT.md) for more troubleshooting.

## 📄 License

Proprietary - Noopur News AI System

## 🤝 Support

For issues or questions:
1. Check documentation files
2. Review TEST_SCENARIOS.md for examples
3. Enable debug logging: `LOG_LEVEL=debug`
4. Check MongoDB and Uniguru dashboards

## 🚦 Status

- ✅ Core System: Production Ready
- ✅ MongoDB Integration: Tested
- ✅ Uniguru API Wrapper: Ready
- ✅ Agent Registry: Operational
- ✅ RL Feedback Loop: Functional
- ✅ LangGraph Pipeline: Implemented
- ✅ BHIV Integration: Ready
- ✅ WebSocket Streaming: Active

## 📊 System Requirements

- **Node.js**: 18.0.0 or higher
- **MongoDB**: 4.4+ (Atlas recommended)
- **RAM**: 512MB minimum, 2GB recommended
- **Disk**: 1GB for logs and temporary storage
- **Network**: Outbound HTTPS for Uniguru/BHIV APIs

---

**Last Updated**: November 2024  
**Version**: 1.0.0  
**Status**: Production Ready

For detailed information, see the comprehensive documentation files included in the repository.
