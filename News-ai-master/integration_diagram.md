# News AI Backend Integration Diagram

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        News AI Backend                              │
│                     + RL Automation Sprint                          │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
           ┌──────────▼──────────┐
           │                     │
           │    FastAPI Server   │◀─────────────────┐
           │    (Port 8000)      │                  │
           └──────────┬──────────┘                  │
                      │                             │
          ┌───────────▼───────────┐                 │
          │                       │                 │
          │   Agent Registry       │                 │
          │   (5 MCP Agents)       │                 │
          └───────────┬───────────┘                 │
                      │                             │
           ┌──────────▼──────────┐                  │
           │                     │                  │
           │  LangGraph Workflow │                  │
           │  Fetch→Verify→Script│                  │
           │  →Feedback→Retry    │                  │
           └──────────┬──────────┘                  │
                      │                             │
           ┌──────────▼──────────┐                  │
           │                     │                  │
           │   RL Feedback Loop  │                  │
           │   (Reward Scoring)  │                  │
           └──────────┬──────────┘                  │
                      │                             │
           ┌──────────▼──────────┐                  │
           │                     │                  │
           │   MongoDB Atlas     │                  │
           │   (News Storage)    │                  │
           └──────────┬──────────┘                  │
                      │                             │
           ┌──────────▼──────────┐                  │
           │                     │                  │
           │   Uniguru AI API    │                  │
           │   Classify/Sentiment│                  │
           │   /Summarize        │                  │
           └──────────┬──────────┘                  │
                      │                             │
           ┌──────────▼──────────┐                  │
           │                     │                  │
           │   BHIV Core Push    │                  │
           │   (TTV/Vaani)       │                  │
           └──────────┬──────────┘                  │
                      │                             │
           ┌──────────▼──────────┐                  │
           │                     │                  │
           │  WebSocket Server   │                  │
           │  (Port 8765)        │                  │
           └─────────────────────┘                  │
                                                    │
┌───────────────────────────────────────────────────┘
│
│ External Systems Integration
│
├── News Sources (URLs/APIs)
├── Seeya Orchestration Layer
├── TTV/Vaani Video Systems
└── Monitoring & Analytics
```

## 🔄 Data Flow

```
News URL Input
        │
        ▼
   Web Scraping
   (BeautifulSoup)
        │
        ▼
  Content Extraction
  (Enhanced Parsing)
        │
        ▼
   Uniguru Classification
   (Categories & Topics)
        │
        ▼
   Sentiment Analysis
   (Polarity & Confidence)
        │
        ▼
   Authenticity Vetting
   (Fact-checking & Bias)
        │
        ▼
   AI Summarization
   (Concise & Structured)
        │
        ▼
   Video Prompt Generation
   (AI Script Creation)
        │
        ▼
   RL Feedback Scoring
   (Tone + Engagement + Quality)
        │
        ▼
   Quality Gate Check
   (Score ≥ 0.6 → Pass)
        │
        ▼
   MongoDB Storage
   (Raw → Verified → Published)
        │
        ▼
   BHIV Core Push
   (Channel × Avatar Matrix)
        │
        ▼
   WebSocket Broadcast
   (Real-time Updates)
        │
        ▼
   Seeya Orchestration
   (Workflow Coordination)
```

## 🤖 Agent Architecture

```
Agent Registry
├── Fetch Agent
│   ├── Web Scraping
│   ├── Content Extraction
│   └── Metadata Parsing
│
├── Filter Agent
│   ├── Relevance Scoring
│   ├── Content Filtering
│   └── Quality Assessment
│
├── Verify Agent
│   ├── Authenticity Analysis
│   ├── Source Credibility
│   └── Fact-checking
│
├── Script Agent
│   ├── Video Prompt Generation
│   ├── Content Adaptation
│   └── Format Optimization
│
└── RL Feedback Agent
    ├── Reward Calculation
    ├── Performance Analysis
    └── Adaptive Learning
```

## 📊 RL Feedback Loop

```
Content Output ──► RL Scoring Engine
                        │
                        ▼
            ┌─────────────────────┐
            │   Reward Function   │
            │                     │
            │ Tone (30%)          │
            │ Engagement (40%)    │
            │ Quality (30%)       │
            └─────────┬───────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │   Quality Gate      │
            │                     │
            │ Score ≥ 0.6 ?       │
            └─────────┬───────────┘
                      │
            ┌─────────┴───────────┐
            │                    │
       PASS │                    │ FAIL
            │                    │
            ▼                    ▼
   ┌─────────────────┐  ┌─────────────────┐
   │   Accept Output  │  │   Auto-Retry    │
   │   → BHIV Push    │  │   → Uniguru     │
   └─────────────────┘  │   Reprocessing   │
                        └─────────────────┘
```

## 🌐 API Endpoints Map

```
FastAPI Server (localhost:8000)
├── /health - System health check
├── /api/
│   ├── comprehensive-news-analysis - Full pipeline
│   ├── automator/process - LangGraph workflow
│   ├── agents - Agent registry
│   ├── rl/feedback - RL scoring
│   ├── uniguru/* - AI services
│   ├── bhiv/push - Core integration
│   └── news/store - MongoDB operations
│
WebSocket Server (localhost:8765)
└── /ws/updates - Real-time updates
```

## 🔗 Integration Points

### Input Sources
- **News URLs**: Direct web scraping
- **API Feeds**: Structured data ingestion
- **Social Media**: Twitter/X content processing
- **RSS Feeds**: Automated content discovery

### Output Destinations
- **BHIV Core**: Video generation pipeline
- **TTV System**: Text-to-video conversion
- **Vaani Platform**: Voice synthesis integration
- **Seeya Orchestration**: Workflow coordination

### Monitoring & Analytics
- **Performance Metrics**: Latency, success rates
- **RL Analytics**: Reward scores, improvement trends
- **Content Analytics**: Authenticity, engagement metrics
- **System Health**: Uptime, error rates, throughput

## 🚀 Deployment Architecture

```
Production Environment
├── Load Balancer (nginx)
├── API Gateway (Kong/Traefik)
├── FastAPI Instances (3+)
├── MongoDB Atlas (Cloud)
├── Redis Cache (Optional)
├── WebSocket Server (Separate)
└── Monitoring Stack
    ├── Prometheus
    ├── Grafana
    └── ELK Stack
```

## 📈 Scaling Considerations

- **Horizontal Scaling**: Multiple FastAPI instances
- **Database Sharding**: MongoDB Atlas auto-scaling
- **Caching Layer**: Redis for frequent queries
- **Queue System**: Celery for async processing
- **CDN Integration**: Static asset delivery

---

*This diagram represents the complete News AI Backend + RL Automation system architecture implemented during the 5-day sprint.*