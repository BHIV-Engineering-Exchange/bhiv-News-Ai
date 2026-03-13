# News AI Backend API Documentation

## Overview

The News AI Backend provides a comprehensive REST API for automated news processing with reinforcement learning capabilities. The API includes 30+ endpoints covering news processing, agent management, RL feedback, and BHIV integration.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication for development. In production, implement API key authentication.

## Core Endpoints

### System Health
- `GET /` - System overview and status
- `GET /api/health` - Comprehensive health check

### News Processing
- `POST /v1/run_pipeline` - **NEW** Unified production pipeline (Fetch→Filter→Verify→Script→RL→BHIV→Audio→Frontend)
- `POST /api/process-news` - Complete news processing pipeline
- `POST /api/automator/process` - LangGraph automation execution

### Agent Management
- `GET /api/agents` - List all MCP agents
- `POST /api/agents/{agent_id}/task` - Submit task to specific agent
- `GET /api/tasks/{task_id}` - Get task status and results

### RL Feedback System
- `POST /api/rl/feedback` - Calculate reward scores
- `GET /api/rl/metrics` - Get feedback analytics

### Uniguru AI Integration
- `POST /api/uniguru/classify` - Text classification
- `POST /api/uniguru/sentiment` - Sentiment analysis
- `POST /api/uniguru/summarize` - Text summarization

### BHIV Core Integration
- `POST /api/bhiv/push` - Push to single channel/avatar
- `POST /api/bhiv/matrix-push` - 3×3 matrix push testing
- `GET /api/bhiv/status` - BHIV connectivity check
- `GET /api/bhiv/history` - Push history

### Database Operations
- `GET /api/news` - Retrieve news items
- `GET /api/news/{item_id}` - Get specific news item

### Real-time Features
- `GET /api/websocket/stats` - WebSocket connection statistics

## Detailed Endpoint Specifications

### POST /v1/run_pipeline

**PRODUCTION ENDPOINT** - Unified pipeline for complete News AI processing including audio generation.

**Request Body:**
```json
{
  "url": "https://example.com/news-article",
  "options": {
    "enable_bhiv_push": true,
    "enable_audio": true,
    "channels": ["news_channel_1"],
    "avatars": ["avatar_alice"],
    "voice": "default",
    "force_correction": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "pipeline": "unified_v1",
  "data": {
    "news_item": {
      "title": "Breaking News Title",
      "content": "Full article content...",
      "summary": "Article summary...",
      "categories": ["technology"],
      "sentiment": {
        "sentiment": "neutral",
        "polarity": 0.1,
        "confidence": 0.8
      },
      "authenticity_score": 85
    },
    "script": {
      "video_prompt": "Video script content...",
      "tone": "neutral",
      "language": "en",
      "avatar_ready": true
    },
    "rl_feedback": {
      "reward_score": 0.82,
      "quality_gate_passed": true,
      "corrections_applied": 0
    },
    "bhiv_push": {
      "successful": true,
      "channels": ["news_channel_1"],
      "successful_pushes": 1
    },
    "audio": {
      "generated": true,
      "audio_url": "https://audio.news-ai.com/generated/12345.mp3",
      "duration": 45.2,
      "voice": "default"
    }
  },
  "processing_metrics": {
    "total_time": 8.5,
    "pipeline_version": "v1.0",
    "components_used": ["automator", "rl", "bhiv", "audio"]
  },
  "preview_ready": true,
  "timestamp": "2025-11-29T07:00:00.000Z"
}
```

### POST /api/process-news

Process a news URL through the complete pipeline.

**Request Body:**
```json
{
  "url": "https://example.com/news-article",
  "enable_full_pipeline": true,
  "enable_bhiv_push": false,
  "channel": "news_channel_1",
  "avatar": "avatar_alice"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Breaking News Title",
    "content": "Full article content...",
    "summary": "Article summary...",
    "authenticity_score": 85,
    "categories": ["technology", "ai"],
    "sentiment_analysis": {
      "sentiment": "neutral",
      "polarity": 0.1,
      "confidence": 0.8
    },
    "video_script": "Video script content...",
    "reward_score": 0.82,
    "processing_metrics": {
      "total_steps": 6,
      "retries_used": 0,
      "processing_time": 2.3
    }
  },
  "message": "News processing completed",
  "timestamp": "2025-11-25T08:00:00.000Z"
}
```

### GET /api/agents

List all registered MCP agents.

**Response:**
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "id": "fetch_agent",
        "name": "News Fetch Agent",
        "role": "fetch",
        "capabilities": ["web_scraping", "content_extraction"],
        "priority": 1,
        "status": "active"
      },
      {
        "id": "filter_agent",
        "name": "Content Filter Agent",
        "role": "filter",
        "capabilities": ["relevance_scoring", "quality_filtering"],
        "priority": 2,
        "status": "active"
      },
      {
        "id": "verify_agent",
        "name": "Authenticity Verify Agent",
        "role": "verify",
        "capabilities": ["fact_checking", "authenticity_analysis"],
        "priority": 3,
        "status": "active"
      },
      {
        "id": "script_agent",
        "name": "Video Script Agent",
        "role": "script",
        "capabilities": ["video_prompts", "content_adaptation"],
        "priority": 4,
        "status": "active"
      },
      {
        "id": "rl_feedback_agent",
        "name": "RL Feedback Agent",
        "role": "feedback",
        "capabilities": ["reward_scoring", "quality_improvement"],
        "priority": 5,
        "status": "active"
      }
    ],
    "total_agents": 5,
    "registry_status": "active"
  },
  "timestamp": "2025-11-25T08:00:00.000Z"
}
```

### POST /api/rl/feedback

Calculate RL feedback for content quality.

**Request Body:**
```json
{
  "news_item": {
    "title": "News Title",
    "content": "Article content...",
    "authenticity_score": 85
  },
  "script_output": {
    "video_script": "Generated video script..."
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "news_item_id": "temp_1732516800.0",
    "reward_score": 0.82,
    "tone_score": 0.85,
    "engagement_score": 0.75,
    "quality_score": 0.90,
    "correction_needed": false,
    "correction_attempts": 0,
    "final_output": {
      "title": "News Title",
      "content": "Article content...",
      "script": "Generated video script...",
      "authenticity_score": 85
    },
    "metrics": {
      "content_length": 1250,
      "script_length": 180,
      "processing_timestamp": "2025-11-25T08:00:00.000Z",
      "reward_components": {
        "tone_weight": 0.3,
        "engagement_weight": 0.4,
        "quality_weight": 0.3
      }
    }
  },
  "timestamp": "2025-11-25T08:00:00.000Z"
}
```

### POST /api/bhiv/matrix-push

Push content to channel-avatar matrix (3×3 testing).

**Request Body:**
```json
{
  "content": {
    "id": "news_001",
    "title": "Breaking News",
    "content": "Article content...",
    "summary": "Article summary...",
    "authenticity_score": 85,
    "video_script": "Video script..."
  },
  "channels": ["news_channel_1", "news_channel_2", "news_channel_3"],
  "avatars": ["avatar_alice", "avatar_bob", "avatar_charlie"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "matrix_push_complete": true,
    "total_combinations": 9,
    "successful_pushes": 9,
    "success_rate": 1.0,
    "results": [
      {
        "channel": "news_channel_1",
        "avatar": "avatar_alice",
        "success": true,
        "push_id": "push_12345",
        "error": ""
      }
    ],
    "completed_at": "2025-11-25T08:00:00.000Z"
  },
  "message": "Matrix push completed: 9/9 successful",
  "timestamp": "2025-11-25T08:00:00.000Z"
}
```

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2025-11-25T08:00:00.000Z"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

Currently no rate limiting implemented. In production, consider implementing:
- Per-IP rate limiting
- API key-based quotas
- Request throttling

## WebSocket Integration

Real-time updates available via WebSocket:

**Connection:** `ws://localhost:8765`

**Message Types:**
- `connection_established` - Connection confirmation
- `bhiv_push` - Push completion notifications
- `matrix_push_complete` - Matrix push results
- `processing_update` - Pipeline progress updates

## Data Models

### NewsItem
```python
{
  "id": "string",
  "url": "string",
  "title": "string",
  "content": "string",
  "summary": "string",
  "authenticity_score": 0-100,
  "categories": ["string"],
  "sentiment_analysis": {
    "sentiment": "string",
    "polarity": -1.0 to 1.0,
    "confidence": 0.0 to 1.0
  },
  "video_script": "string",
  "reward_score": 0.0 to 1.0,
  "scraped_at": "ISO datetime",
  "verified_at": "ISO datetime",
  "published_at": "ISO datetime"
}
```

### AgentTask
```python
{
  "id": "string",
  "agent_id": "string",
  "task_data": {},
  "status": "pending|processing|completed|failed",
  "result": {},
  "error": "string",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

### RLFeedback
```python
{
  "news_item_id": "string",
  "reward_score": 0.0 to 1.0,
  "tone_score": 0.0 to 1.0,
  "engagement_score": 0.0 to 1.0,
  "quality_score": 0.0 to 1.0,
  "correction_needed": boolean,
  "correction_attempts": integer,
  "metrics": {
    "content_length": integer,
    "script_length": integer,
    "processing_timestamp": "ISO datetime"
  }
}
```

## Performance Expectations

- **Average Latency**: <5 seconds for complete pipeline
- **Success Rate**: >95% for valid news sources
- **Concurrent Connections**: 100+ simultaneous users
- **Uptime**: 99.9% availability

## Monitoring

Use these endpoints for system monitoring:
- `GET /api/health` - Overall system health
- `GET /api/rl/metrics` - RL performance metrics
- `GET /api/bhiv/history` - Push operation history
- `GET /api/websocket/stats` - WebSocket connection stats

## Production Deployment

For production deployment:
1. Set all required environment variables
2. Configure MongoDB Atlas connection
3. Set up BHIV Core integration
4. Implement proper authentication
5. Configure monitoring and logging
6. Set up load balancing and scaling