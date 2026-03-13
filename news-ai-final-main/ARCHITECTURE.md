# Noopur News AI - System Architecture

## System Overview

Noopur News AI is a comprehensive microservice backend for intelligent news processing, featuring:
- MongoDB Atlas-based news pipeline (raw → verified → published)
- Uniguru API integration for content enrichment
- Intelligent Agent Registry with task routing
- Reinforcement Learning feedback loop for quality improvement
- LangGraph-based self-correcting automation pipeline
- BHIV integration with WebSocket streaming

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOOPUR NEWS AI SYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐                                                 │
│  │  REST API   │  POST /api/news (Raw News Ingestion)          │
│  │ Port 3000   │  GET /api/news/:id (Retrieve)                 │
│  └──────┬──────┘  PUT /api/news/:id (Update)                   │
│         │         GET /api/news/status/:status (Query)          │
│         │                                                        │
│    ┌────▼──────────────────────────────────────────────────┐    │
│    │          🗄️  MONGODB ATLAS (News Database)             │    │
│    ├───────────────────────────────────────────────────────┤    │
│    │  ┌──────────────────┐  ┌──────────────────────────┐   │    │
│    │  │  news_items      │  │  agent_tasks             │   │    │
│    │  │  ├─ Raw          │  │  ├─ Pending              │   │    │
│    │  │  ├─ Verified     │  │  ├─ Processing           │   │    │
│    │  │  ├─ Published    │  │  ├─ Completed            │   │    │
│    │  │  └─ Enrichment   │  │  └─ Failed/Retry         │   │    │
│    │  └──────────────────┘  └──────────────────────────┘   │    │
│    │  ┌──────────────────┐  ┌──────────────────────────┐   │    │
│    │  │  feedback_metrics│  │  Processing Logs         │   │    │
│    │  │  ├─ Reward Score │  │  └─ Audit Trail          │   │    │
│    │  │  ├─ Corrections  │  │                          │   │    │
│    │  │  └─ Latencies    │  │                          │   │    │
│    │  └──────────────────┘  └──────────────────────────┘   │    │
│    └───────────────────────────────────────────────────────┘    │
│         ▲                                                        │
│         │                                                        │
│    ┌────┴──────────────────────────────────────────────────┐    │
│    │  🤖 AGENT REGISTRY (MCP CORE)                         │    │
│    ├───────────────────────────────────────────────────────┤    │
│    │                                                        │    │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │    │
│    │  │  Fetch   │  │ Filter   │  │ Verify   │            │    │
│    │  │ Agent    │  │ Agent    │  │ Agent    │            │    │
│    │  │(Prio: 10)│  │(Prio: 8) │  │(Prio: 9) │            │    │
│    │  └──────────┘  └──────────┘  └──────────┘            │    │
│    │                                                        │    │
│    │  ┌──────────┐  ┌──────────┐                           │    │
│    │  │ Script   │  │RLFeedback│                           │    │
│    │  │ Agent    │  │ Agent    │                           │    │
│    │  │(Prio: 7) │  │(Prio: 6) │                           │    │
│    │  └──────────┘  └──────────┘                           │    │
│    │                                                        │    │
│    │  • Async Task Routing                                 │    │
│    │  • Retry Logic (3 retries, exponential backoff)       │    │
│    │  • Queue Management                                   │    │
│    │  • Agent Health Status                                │    │
│    └───────────────────────────────────────────────────────┘    │
│         ▲                                                        │
│         │                                                        │
│    ┌────┴──────────────────────────────────────────────────┐    │
│    │  🧠 UNIGURU ENRICHMENT SERVICE                        │    │
│    ├───────────────────────────────────────────────────────┤    │
│    │                                                        │    │
│    │  ┌──────────────────┐  ┌──────────────────────────┐  │    │
│    │  │ Classification   │  │ Sentiment Analysis       │  │    │
│    │  │ (Category,       │  │ (Label, Score, Aspects)  │  │    │
│    │  │  Subcategory,    │  │ (Confidence, Aspects)    │  │    │
│    │  │  Confidence)     │  │                          │  │    │
│    │  └──────────────────┘  └──────────────────────────┘  │    │
│    │                                                        │    │
│    │  ┌──────────────────────────────────────────────────┐ │    │
│    │  │ Summarization                                    │ │    │
│    │  │ (Short, Medium, Key Points, Entities)            │ │    │
│    │  └──────────────────────────────────────────────────┘ │    │
│    │                                                        │    │
│    │  • Batch Processing Support                           │    │
│    │  • Parallel API Calls (30s timeout)                   │    │
│    │  • Error Handling & Logging                           │    │
│    └───────────────────────────────────────────────────────┘    │
│         ▲                                                        │
│         │                                                        │
│    ┌────┴──────────────────────────────────────────────────┐    │
│    │  💡 RL FEEDBACK LOOP                                  │    │
│    ├───────────────────────────────────────────────────────┤    │
│    │                                                        │    │
│    │  Reward Calculation:                                 │    │
│    │  ├─ Tone Accuracy (40%)                              │    │
│    │  │  • Sentiment confidence                           │    │
│    │  │  • Aspect consistency                             │    │
│    │  │  • Classification confidence                      │    │
│    │  │                                                   │    │
│    │  └─ Engagement Prediction (60%)                      │    │
│    │     • Sentiment boost (+0.2 positive)                │    │
│    │     • Content depth (key points)                     │    │
│    │     • Entity richness                                │    │
│    │     • Category engagement score                      │    │
│    │                                                        │    │
│    │  Threshold: 0.6 (auto-reroute if lower)              │    │
│    │  Auto-Reroute: Re-analyze with Uniguru               │    │
│    │  Metrics Logged: Reward, Corrections %, Latency      │    │
│    └───────────────────────────────────────────────────────┘    │
│         ▲                                                        │
│         │                                                        │
│    ┌────┴──────────────────────────────────────────────────┐    │
│    │  🔄 LANGGRAPH AUTOMATION PIPELINE                     │    │
│    ├───────────────────────────────────────────────────────┤    │
│    │                                                        │    │
│    │  Fetch → Verify → Script → Feedback → [Loop]          │    │
│    │  ├─ Max 3 Iterations per item                         │    │
│    │  ├─ Auto-retry on low reward (< 0.6)                 │    │
│    │  ├─ Adaptive reprocessing                             │    │
│    │  └─ Statistics tracking                               │    │
│    │                                                        │    │
│    │  Success Metrics:                                     │    │
│    │  • Avg Reward Score                                   │    │
│    │  • Success Rate                                       │    │
│    │  • Iterations Required                                │    │
│    │  • Processing Time                                    │    │
│    │                                                        │    │
│    └───────────────────────────────────────────────────────┘    │
│         ▲                                                        │
│         │                                                        │
│    ┌────┴──────────────────────────────────────────────────┐    │
│    │  🌐 BHIV INTEGRATION & STREAMING                      │    │
│    ├───────────────────────────────────────────────────────┤    │
│    │                                                        │    │
│    │  ┌──────────────┐  ┌──────────────────────────────┐  │    │
│    │  │ TTV Endpoint │  │ Vaani Endpoint               │  │    │
│    │  │ (Text-to-    │  │ (Voice/Audio Narrative)      │  │    │
│    │  │  Visual)     │  │                              │  │    │
│    │  └──────────────┘  └──────────────────────────────┘  │    │
│    │                                                        │    │
│    │  Batch Publishing:                                   │    │
│    │  • Single item distribution                          │    │
│    │  • Multi-item streaming                              │    │
│    │  • Webhook feedback from BHIV                        │    │
│    │  • Status tracking                                   │    │
│    │                                                        │    │
│    └───────────────────────────────────────────────────────┘    │
│         ▲                                                        │
│         │                                                        │
│         └────────────────────────────────────────────────────┐   │
│                                                              │   │
│  ┌────────────────────────────────────────────────────────┐ │   │
│  │  🌐 WEBSOCKET SERVER (Port 3001)                        │ │   │
│  │  • Real-time status updates                             │ │   │
│  │  • News published events                                │ │   │
│  │  • Stream initiated notifications                       │ │   │
│  │  • BHIV status updates                                  │ │   │
│  └────────────────────────────────────────────────────────┘ │   │
│                                                              │   │
└──────────────────────────────────────────────────────────────┘   
```

## Data Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEWS PROCESSING FLOW                          │
├─────────────────────────────────────────────────────────────────┤

STEP 1: NEWS INGESTION
─────────────────────
  Raw Input
    ↓
  POST /api/news
    ↓
  Create NewsItem (status: 'raw')
    ↓
  Async Enrichment Started (Non-blocking)

STEP 2: UNIGURU ENRICHMENT (Background)
──────────────────────────────────────
  ┌─ Classification
  │  └─ Category, Subcategory, Confidence
  │
  ├─ Sentiment Analysis
  │  └─ Label, Score, Aspects, Confidence
  │
  └─ Summarization
     └─ Short/Medium Summary, Key Points, Entities

  Auto-promote to 'verified' status

STEP 3: AGENT REGISTRY ROUTING
──────────────────────────────
  News Item enters pipeline:
  
  1. FETCH AGENT (Priority 10)
     • Validate data format
     • Confirm source authenticity
     
  2. FILTER AGENT (Priority 8)
     • Duplicate check
     • Language detection
     • Relevance scoring
     
  3. VERIFY AGENT (Priority 9)
     • Fact verification
     • Credibility assessment
     • Cross-reference with entities
     
  4. SCRIPT AGENT (Priority 7)
     • Generate compelling narrative
     • Create headlines/body scripts
     • Set tone appropriately
     
  5. RL FEEDBACK AGENT (Priority 6)
     • Evaluate all outputs
     • Calculate reward score
     • Suggest corrections if needed

STEP 4: RL FEEDBACK EVALUATION
──────────────────────────────
  If Reward Score < 0.6:
    ├─ Identify correction type(s)
    ├─ Auto-reroute to Uniguru
    │  ├─ Sentiment re-analysis
    │  ├─ Summary regeneration
    │  └─ Classification re-check
    └─ Re-evaluate (Loop back)
  
  Else:
    └─ Proceed to publication

STEP 5: BHIV DISTRIBUTION
──────────────────────────
  Publish to Endpoints:
  ├─ TTV (Text-to-Visual)
  │  └─ Headline + Visual narrative
  │
  └─ Vaani (Voice/Audio)
     └─ Key points + entities + tone
  
  Webhook from BHIV:
  └─ Engagement metrics
  └─ User sentiment
  └─ Distribution status

STEP 6: MONITORING & FEEDBACK
──────────────────────────────
  WebSocket broadcast:
  ├─ news_published event
  ├─ stream_initiated event
  └─ bhiv_status_update event
  
  Metrics logged:
  ├─ Reward score
  ├─ Correction percentage
  └─ Latencies

FINAL STATE: NewsItem status = 'published'
```

## Component Responsibilities

### 🗄️ MongoDB Atlas
- **Collections:**
  - `news_items`: Raw news + enrichment + pipeline stages
  - `agent_tasks`: Task tracking and execution metrics
  - `feedback_metrics`: RL feedback data and history
  
- **Indexes:** Status, timestamp, agent_id for query performance
- **TTL**: Optional document expiration for old archived news

### 🤖 Agent Registry (AgentRegistry class)
- **Responsibilities:**
  - Register agents with specific roles and handlers
  - Queue task management
  - Async task execution with timeouts
  - Retry logic with exponential backoff
  - Agent health and status monitoring

### 🧠 Uniguru Service
- **API Integration:**
  - `/classify` - Content classification
  - `/sentiment` - Sentiment analysis
  - `/summarize` - Text summarization
  
- **Features:**
  - Batch processing
  - Parallel API calls
  - Error handling & logging
  - Health check

### 💡 RL Feedback Loop
- **Evaluation Metrics:**
  - Tone Accuracy (40% weight)
  - Engagement Prediction (60% weight)
  
- **Auto-routing:**
  - Identifies failing components
  - Re-processes with Uniguru
  - Iterative improvement
  
- **Metrics Collection:**
  - Reward scores
  - Correction types
  - Processing latencies

### 🔄 LangGraph Pipeline
- **Stages:**
  1. Fetch - Data validation
  2. Verify - Fact checking
  3. Script - Narrative generation
  4. Feedback - Quality evaluation
  
- **Features:**
  - Max 3 iterations
  - Auto-retry on low scores
  - Pipeline statistics
  - History tracking

### 🌐 BHIV Integration
- **Endpoints:**
  - `/ttv/publish` - Single item to Text-to-Visual
  - `/vaani/publish` - Single item to Voice/Audio
  - `/ttv/batch` - Batch to TTV
  - `/vaani/batch` - Batch to Vaani
  
- **Webhook Receiver:**
  - Status updates
  - Engagement metrics
  - User feedback

### 📡 WebSocket Server
- **Real-time Events:**
  - News publication notifications
  - Stream initiation alerts
  - BHIV status updates
  - System metrics streaming

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         NODE.JS APPLICATION             │
├─────────────────────────────────────────┤
│  Express (Port 3000)                    │
│  └─ REST API Routes                     │
│     ├─ /api/news                        │
│     ├─ /api/bhiv                        │
│     └─ /api/system                      │
│                                         │
│  WebSocket Server (Port 3001)           │
│  └─ Real-time streaming                 │
└─────────────────────────────────────────┘
         │           │           │
         ↓           ↓           ↓
    ┌────────┐  ┌─────────┐  ┌───────┐
    │MongoDB │  │Uniguru  │  │ BHIV  │
    │ Atlas  │  │   API   │  │ Core  │
    └────────┘  └─────────┘  └───────┘
```

## Scalability Considerations

### Horizontal Scaling
- Multiple instances with shared MongoDB
- Load balancer for REST API (port 3000)
- Separate WebSocket server for real-time updates

### Vertical Scaling
- Increase agent concurrency limits
- Batch processing optimization
- Connection pooling for database

### Performance Optimizations
- Database indexes on frequently queried fields
- Caching layer for Uniguru results
- Queue prioritization
- Async enrichment to avoid blocking

## Error Handling & Recovery

```
Task Execution Error:
  ├─ Immediate Retry (1000ms delay)
  ├─ Second Retry (2000ms delay)
  ├─ Third Retry (4000ms delay)
  └─ Failure → Log + Alert

Low Reward Score:
  ├─ Identify failure type
  ├─ Auto-reroute to Uniguru
  ├─ Re-evaluate
  └─ Log metrics

API Timeouts:
  ├─ 30s default timeout
  ├─ 10s for classification
  ├─ 10s for sentiment
  └─ 10s for summarization
```

## Security Considerations

1. **API Authentication**
   - Bearer token for BHIV endpoints
   - Environment variables for secrets

2. **Data Validation**
   - Input schema validation
   - Content length limits
   - Rate limiting (recommended for production)

3. **Audit Logging**
   - Processing logs in database
   - Error tracking
   - Metrics collection

4. **CORS & Network**
   - Configure CORS for Web clients
   - Internal REST hooks for BHIV
   - WebSocket origin validation

---

*Architecture Last Updated: November 2024*
