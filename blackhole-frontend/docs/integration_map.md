# Integration Map - News AI Frontend

## Overview
This document maps the integration points between the frontend and the three backend services:
- **Sankalp** (Insight Node) - Audio generation, scripts, scoring
- **Noopur** (Backend) - News data and processing endpoints
- **Seeya** (Orchestration) - Pipeline stage tracking

---

## 1. Sankalp (Insight Node) Integration

### Repository
- **GitHub**: https://github.com/sankalp0709/News-AI-.git
- **Type**: Python-based audio generation and ranking service
- **Port**: 8000 (default, configurable via `API_PORT`)

### Endpoints

#### `POST /feedback`
**Purpose**: Submit user feedback for reinforcement learning

**Request Body**:
```json
{
  "id": "https://www.bbc.com/news/articles/c891zkwvjl2o#0",
  "item": {
    "id": "https://www.bbc.com/news/articles/c891zkwvjl2o#0",
    "priority_score": 0.7,
    "trend_score": 1.0
  },
  "signals": {
    "editor_approve": true,
    "user_like": false,
    "user_skip": false,
    "manual_override": false
  }
}
```

**Response**:
```json
{
  "id": "https://www.bbc.com/news/articles/c891zkwvjl2o#0",
  "reward": 1.0,
  "action": "requeue",
  "requeued": true
}
```

**Signal Types** (from `rl_feedback.py`):
- `editor_approve`: +1.0 reward
- `user_like`: +0.6 reward
- `user_skip`: -0.4 reward
- `manual_override`: -0.8 reward

#### `POST /requeue`
**Purpose**: Manually requeue an item for reprocessing

**Request Body**:
```json
{
  "id": "https://www.bbc.com/news/articles/c891zkwvjl2o#0"
}
```

**Response**:
```json
{
  "id": "https://www.bbc.com/news/articles/c891zkwvjl2o#0",
  "requeued": true
}
```

### Data Schema (Integration Format)

From `sample_integration.json` and `weekly_report.json`:

```typescript
interface SankalpItem {
  id: string;                    // URL-based unique identifier
  script: string;                // Text for audio (use summary_medium)
  tone: string;                  // "joyful", "calm", etc.
  language: string;              // "en", etc.
  audio_path: string;           // Relative path to audio file
  priority_score: number;        // 0.0 - 1.0 (ranking score)
  trend_score: number;           // 0.0 - 1.0 (trending score)
  
  // Additional fields from weekly_report.json:
  title?: string;
  summary_short?: string;
  summary_medium?: string;
  category?: string;
  polarity?: string;             // "positive", "negative", "neutral"
  timestamp?: string;            // ISO 8601 format
  audio_duration?: number;      // Duration in seconds
  voice_used?: string;
  synthesis_status?: string;     // "fallback", "vaani", etc.
  avatar?: string;              // "dev", "asha", "kiran"
}
```

### Feed Endpoint (Expected)
**Note**: Sankalp exports to `exports/weekly_report.json` but doesn't expose a GET endpoint. We need to:
1. Check with Sankalp if they expose a GET endpoint for the feed
2. Or consume the JSON file directly if hosted
3. Or integrate via Noopur if Noopur aggregates Sankalp data

### Audio File Access
- Audio files are stored at paths like: `data/audio/20251117/dev/item_6_dev.wav`
- Paths are normalized to use forward slashes
- Need to determine if audio files are served via HTTP or need file system access

---

## 2. Noopur (Backend) Integration

### Endpoints (Expected - To Confirm)

#### `GET /news`
**Purpose**: Fetch list of processed news items

**Expected Response**:
```json
{
  "items": [
    {
      "id": "...",
      "title": "...",
      "summary": "...",
      "category": "...",
      "timestamp": "...",
      // ... other fields
    }
  ]
}
```

#### `GET /processed/:id`
**Purpose**: Get detailed information for a specific processed item

**Expected Response**:
```json
{
  "id": "...",
  "title": "...",
  "summary": "...",
  "category": "...",
  "timestamp": "...",
  "audio_path": "...",
  "priority_score": 0.7,
  "trend_score": 1.0,
  // ... full item details
}
```

#### `GET /audio/:id`
**Purpose**: Get audio file URL or stream for an item

**Expected Response**:
```json
{
  "id": "...",
  "audio_url": "https://...",
  "audio_path": "data/audio/...",
  "duration": 9.52
}
```

### Authentication
- **Method**: To be confirmed with Noopur
- **Expected**: JWT token in `Authorization: Bearer <token>` header

---

## 3. Seeya (Orchestration) Integration

### Pipeline Stages (Expected - To Confirm)

The pipeline should track these stages:
1. **Fetched** - News article ingested
2. **Filtered** - Content filtered/cleaned
3. **Summarized** - Summary generated
4. **Verified** - Authenticity checked
5. **Scripted** - Script prepared for TTS
6. **Voiced** - Audio generated

### Endpoint (Expected - To Confirm)

#### `GET /pipeline/:id` or `GET /item/:id/stages`
**Purpose**: Get pipeline stage information for an item

**Expected Response**:
```json
{
  "id": "...",
  "stages": [
    {
      "name": "Fetched",
      "status": "completed",
      "timestamp": "2025-11-17T02:59:09+00:00"
    },
    {
      "name": "Filtered",
      "status": "completed",
      "timestamp": "2025-11-17T02:59:15+00:00"
    },
    {
      "name": "Summarized",
      "status": "completed",
      "timestamp": "2025-11-17T02:59:25+00:00"
    },
    {
      "name": "Verified",
      "status": "completed",
      "timestamp": "2025-11-17T02:59:30+00:00"
    },
    {
      "name": "Scripted",
      "status": "completed",
      "timestamp": "2025-11-17T02:59:35+00:00"
    },
    {
      "name": "Voiced",
      "status": "completed",
      "timestamp": "2025-11-17T02:59:45+00:00"
    }
  ]
}
```

---

## Frontend Component Mapping

### News Feed Component
**Data Source**: `GET /news` (Noopur) or Sankalp's `weekly_report.json`

**Fields to Display**:
- `title` → Card title
- `summary_medium` or `script` → Card description
- `category` → Category badge
- `priority_score` → Sorting/ranking
- `trend_score` → Trending indicator
- `audio_path` → Audio player source
- `timestamp` → Published date

### Audio Player Component
**Data Source**: `audio_path` from item

**Implementation**:
- Use `audio_path` to construct audio URL
- Support play/pause controls
- Display `audio_duration` if available
- Handle missing audio gracefully

### Pipeline Timeline Component
**Data Source**: `GET /pipeline/:id` (Seeya)

**Visualization**:
- Show 6 stages: Fetched → Filtered → Summarized → Verified → Scripted → Voiced
- Use `status` and `timestamp` to show progress
- Animate transitions between stages

### Feedback Component
**Data Source**: `POST /feedback` (Sankalp)

**Actions**:
- **Approve** → `{ editor_approve: true }`
- **Like** → `{ user_like: true }`
- **Skip** → `{ user_skip: true }`
- **Flag** → `{ manual_override: true }`

**Implementation**:
- Send feedback immediately on click
- Show optimistic UI update
- Store in localStorage for offline sync
- Retry on reconnect

---

## Environment Variables

### Required (`.env.local`)
```env
# Noopur Backend
NEXT_PUBLIC_NOOPUR_API_BASE=http://localhost:8001
NEXT_PUBLIC_NOOPUR_API_KEY=your_api_key_here

# Sankalp Insight Node
NEXT_PUBLIC_SANKALP_API_BASE=http://localhost:8000
NEXT_PUBLIC_SANKALP_API_KEY=your_api_key_here

# Seeya Orchestration
NEXT_PUBLIC_SEEYA_API_BASE=http://localhost:8002
NEXT_PUBLIC_SEEYA_API_KEY=your_api_key_here

# Security (SSPL-III)
NEXT_PUBLIC_JWT_TOKEN=your_jwt_token_here
NEXT_PUBLIC_HMAC_SECRET=your_hmac_secret_here

# Audio Files
NEXT_PUBLIC_AUDIO_BASE_URL=http://localhost:8000/data/audio
```

---

## Questions for Sync Calls

### Sankalp
1. ✅ Confirmed: `audio_path`, `script`, `priority_score`, `trend_score` fields exist
2. ❓ Do you expose a GET endpoint for the feed, or should we consume `weekly_report.json`?
3. ❓ How are audio files served? HTTP endpoint or file system path?
4. ❓ What's the expected format for `signals` in `/feedback`? Can we send multiple signals at once?
5. ❓ What port does the API server run on by default?

### Noopur
1. ❓ Confirm `/news` and `/processed/:id` endpoint URLs and response formats
2. ❓ What authentication method do you use? JWT? API key?
3. ❓ Do you aggregate data from Sankalp, or should we call both services?
4. ❓ What's the `/audio/:id` endpoint format?

### Seeya
1. ❓ Confirm pipeline stage endpoint URL and format
2. ❓ What are the exact stage names and status values?
3. ❓ How do we get pipeline status for an item? Is it included in the item data or separate endpoint?

---

## Next Steps

1. ✅ Clone and understand Sankalp repository
2. ⏳ Schedule sync calls with Sankalp, Noopur, Seeya
3. ⏳ Create `.env.local.example` file
4. ⏳ Start implementing API wrappers in `lib/api.js`

---

## References

- Sankalp Repo: https://github.com/sankalp0709/News-AI-.git
- Sample Integration JSON: `sankalp-insight-node/exports/sample_integration.json`
- Weekly Report JSON: `sankalp-insight-node/exports/weekly_report.json`
- API Server: `sankalp-insight-node/scripts/api_server.py`
- RL Feedback: `sankalp-insight-node/agents/rl_feedback.py`

