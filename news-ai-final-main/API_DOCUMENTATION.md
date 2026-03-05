# Noopur News AI - Complete API Documentation

## Base URLs

- **REST API**: `http://localhost:3000`
- **WebSocket**: `ws://localhost:3001`

## Authentication

All BHIV endpoints require:
```
Authorization: Bearer <BHIV_API_KEY>
Content-Type: application/json
```

---

## 📰 News Endpoints

### 1. Create Raw News Item

**POST** `/api/news`

Create a new raw news item. Uniguru enrichment (classification, sentiment, summarization) starts automatically in background.

**Request:**
```json
{
  "title": "Breaking News Title",
  "content": "Full article content...",
  "source": "api|rss|manual|social",
  "sourceUrl": "https://example.com/news"
}
```

**Response:**
```json
{
  "success": true,
  "message": "News item created and enrichment started",
  "newsId": "507f1f77bcf86cd799439011",
  "status": "raw"
}
```

### 2. Get News Item

**GET** `/api/news/:id`

Retrieve a specific news item with full enrichment data.

**Response:**
```json
{
  "success": true,
  "data": {
    "_id": "507f1f77bcf86cd799439011",
    "title": "...",
    "content": "...",
    "status": "verified",
    "classification": {
      "category": "Technology",
      "subcategory": "AI",
      "confidence": 0.95
    },
    "sentiment": {
      "label": "positive",
      "score": 0.78,
      "confidence": 0.92
    },
    "summary": {
      "short": "...",
      "medium": "...",
      "keyPoints": ["...", "..."],
      "entities": [{"type": "ORG", "value": "..."}]
    },
    "verification": {
      "verified": true,
      "verificationScore": 0.88
    },
    "feedback": {
      "rewardScore": 0.82,
      "toneAccuracy": 0.85,
      "engagementPrediction": 0.79
    }
  }
}
```

### 3. Get News by Status

**GET** `/api/news/status/:status`

Get all news items with specific status.

**Parameters:**
- `:status` - One of: `raw`, `verified`, `published`

**Response:**
```json
{
  "success": true,
  "status": "published",
  "count": 5,
  "data": [...]
}
```

### 4. Update News Item

**PUT** `/api/news/:id`

Update news item (usually after verification/feedback).

**Request:**
```json
{
  "status": "verified|published",
  "verification": {
    "verified": true,
    "verificationScore": 0.9,
    "verificationNotes": "..."
  },
  "feedback": {
    "rewardScore": 0.85,
    "toneAccuracy": 0.88
  }
}
```

---

## 🤖 Agent Registry Endpoints

### 1. Submit Task to Agent

**Internal method** - Used by system. See AgentRegistry class.

```javascript
await agentRegistry.submitTask(
  newsItemId,      // Target news item
  agentRole,       // 'fetch'|'filter'|'verify'|'script'|'rlfeedback'
  payload,         // Task data
  priority         // 0-10
);
```

### 2. Get Agent Status

**GET** `/api/system/info`

Get all agents and their queue status.

**Response:**
```json
{
  "system": "Noopur News AI",
  "agents": {
    "total": 5,
    "byRole": {
      "fetch": 1,
      "filter": 1,
      "verify": 1,
      "script": 1,
      "rlfeedback": 1
    }
  }
}
```

---

## 📊 RL Feedback Loop Endpoints

### 1. Evaluate Output

**Internal method** - Called automatically after each pipeline stage.

```javascript
const evaluation = await rlFeedbackLoop.evaluateOutput(
  newsItemId,
  uniguruService
);

// Returns:
{
  rewardScore: 0.82,
  toneAccuracy: 0.85,
  engagementPrediction: 0.79,
  correctionsNeeded: false,
  correctionTypes: [],
  metrics: {...}
}
```

### 2. Get Feedback Metrics

**GET** `/api/feedback/metrics?newsItemId=507f1f77bcf86cd799439011`

Get RL feedback metrics for a news item.

**Response:**
```json
{
  "success": true,
  "data": {
    "newsItemId": "507f1f77bcf86cd799439011",
    "rewardScore": 0.82,
    "toneAccuracy": 0.85,
    "engagementPrediction": 0.79,
    "correctionMetrics": {
      "totalCorrections": 1,
      "correctionTypes": {
        "tone": 0,
        "sentiment": 1,
        "summary": 0,
        "classification": 0
      },
      "correctionPercentage": 100
    },
    "latency": {
      "totalLatency": 5234,
      "classificationLatency": 1200,
      "sentimentLatency": 1400,
      "summarizationLatency": 1300
    }
  }
}
```

---

## 🔄 LangGraph Pipeline Endpoints

### 1. Process News Through Pipeline

**POST** `/api/bhiv/process`

Process a news item through complete pipeline (Fetch → Verify → Script → Feedback → Publish).

**Request:**
```json
{
  "newsItemId": "507f1f77bcf86cd799439011",
  "distribution": {
    "ttv": true,
    "vaani": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "News processed and sent to BHIV",
  "pipelineResult": {
    "newsItemId": "507f1f77bcf86cd799439011",
    "success": true,
    "finalRewardScore": 0.85,
    "iterations": 1,
    "processingTime": 4523
  },
  "bhivResult": {
    "status": "completed",
    "ttv": {
      "success": true,
      "status": "delivered",
      "messageId": "msg_123"
    },
    "vaani": {
      "success": true,
      "status": "delivered",
      "messageId": "msg_124"
    }
  }
}
```

### 2. Get Pipeline Statistics

**GET** `/api/system/info`

Returns pipeline statistics including success rate, average reward score, and processing times.

**Response:**
```json
{
  "system": "Noopur News AI",
  "pipeline": {
    "totalProcessed": 10,
    "successful": 9,
    "failed": 1,
    "averageRewardScore": 0.84,
    "averageIterations": 1.2,
    "averageProcessingTime": 4200,
    "successRate": "90.00%"
  }
}
```

---

## 📡 BHIV Integration Endpoints

### 1. Send to BHIV (TTV and Vaani)

**POST** `/api/bhiv/process`

Process and distribute news to BHIV endpoints (see LangGraph section).

### 2. Stream Multiple News Items

**POST** `/api/bhiv/stream`

Stream multiple published news items to BHIV.

**Request:**
```json
{
  "target": "ttv|vaani",
  "newsItemIds": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"],
  "filter": {
    "status": "published"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Streamed 2 items to ttv",
  "streamResult": {
    "success": true,
    "status": "completed",
    "processed": 2,
    "batchId": "batch-1699564800000"
  }
}
```

### 3. Receive BHIV Webhook

**POST** `/api/bhiv/webhook`

BHIV sends status updates back via webhook.

**Request from BHIV:**
```json
{
  "newsItemId": "507f1f77bcf86cd799439011",
  "status": "delivered",
  "metrics": {
    "engagement": 0.92,
    "reach": 50000
  },
  "feedback": {
    "userSentiment": "positive"
  }
}
```

### 4. Get BHIV Distribution Status

**GET** `/api/bhiv/status/:newsItemId`

Check distribution status across BHIV endpoints.

**Response:**
```json
{
  "success": true,
  "newsItemId": "507f1f77bcf86cd799439011",
  "distribution": {
    "ttv": true,
    "vaani": true,
    "other": []
  },
  "publishedAt": "2024-11-10T15:30:00Z",
  "status": "published"
}
```

---

## 🌐 WebSocket Events

### Connection & Subscription

```javascript
// Connect
const ws = new WebSocket('ws://localhost:3001');

// Subscribe to news updates
ws.send(JSON.stringify({
  type: 'subscribe',
  newsItemId: '507f1f77bcf86cd799439011'
}));

// Request pipeline stats
ws.send(JSON.stringify({
  type: 'request_stats'
}));

// Request agent queue status
ws.send(JSON.stringify({
  type: 'request_agents'
}));
```

### Broadcast Events (Server → Client)

#### News Published
```json
{
  "type": "news_published",
  "data": {
    "newsItemId": "507f1f77bcf86cd799439011",
    "status": "published",
    "reward": 0.85,
    "bhivStatus": "delivered"
  },
  "timestamp": "2024-11-10T15:30:00Z"
}
```

#### Stream Initiated
```json
{
  "type": "stream_initiated",
  "data": {
    "target": "ttv",
    "itemsStreamed": 5,
    "status": "completed"
  },
  "timestamp": "2024-11-10T15:31:00Z"
}
```

#### BHIV Status Update
```json
{
  "type": "bhiv_status_update",
  "data": {
    "newsItemId": "507f1f77bcf86cd799439011",
    "status": "delivered",
    "metrics": {
      "engagement": 0.92,
      "reach": 50000
    }
  },
  "timestamp": "2024-11-10T15:32:00Z"
}
```

---

## 🏥 Health & System Endpoints

### Health Check

**GET** `/health`

System health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-10T15:30:00Z",
  "services": {
    "database": "connected",
    "uniguru": "initialized",
    "agents": 5,
    "pipeline": "ready"
  }
}
```

### System Info

**GET** `/api/system/info`

Complete system status and statistics.

---

## 🔑 Error Responses

All endpoints follow standard error format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Server Error

---

## 📊 Data Flow

```
Raw News
   ↓
[POST /api/news] → Create + Start Enrichment
   ↓
Uniguru API (async)
   - Classification
   - Sentiment Analysis
   - Summarization
   ↓
[GET /api/news/:id] → Retrieve Enriched Data
   ↓
[POST /api/bhiv/process] → Process Pipeline
   ├─ Fetch Agent
   ├─ Verify Agent
   ├─ Script Agent
   └─ RL Feedback Agent
   ↓
RL Feedback Loop (Score < 0.6)
   ├─ Re-analyze Sentiment
   ├─ Re-summarize
   └─ Re-classify
   ↓
[POST /api/bhiv/stream] → Distribute
   ├─ TTV Endpoint
   └─ Vaani Endpoint
   ↓
[POST /api/bhiv/webhook] ← BHIV Status
   ↓
WebSocket Broadcast
```

---

## 🚀 Example Workflows

### Complete News Processing

```bash
# 1. Create news
curl -X POST http://localhost:3000/api/news \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Breaking: AI Breakthrough",
    "content": "Researchers announce...",
    "source": "api"
  }'

# Response: {"newsId": "xxx"}

# 2. Wait for enrichment (check periodically)
curl http://localhost:3000/api/news/xxx

# 3. Process through pipeline
curl -X POST http://localhost:3000/api/bhiv/process \
  -H "Content-Type: application/json" \
  -d '{
    "newsItemId": "xxx",
    "distribution": {"ttv": true, "vaani": true}
  }'

# 4. Monitor via WebSocket
wscat -c ws://localhost:3001
> {"type": "subscribe", "newsItemId": "xxx"}
```

---

## 📋 Configuration

See `.env.example` for all configuration options:

```
MONGODB_URI=mongodb+srv://...
UNIGURU_API_KEY=...
UNIGURU_BASE_URL=...
BHIV_API_URL=...
BHIV_API_KEY=...
PORT=3000
WS_PORT=3001
LOG_LEVEL=debug
```

---

Last Updated: November 10, 2024
