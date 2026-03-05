# Noopur News AI - Advanced News Processing System

A comprehensive microservice backend for intelligent news processing with:
- MongoDB Atlas integration for raw → verified → published news pipeline
- Uniguru API integration (classification, sentiment, summarization)
- Agent Registry (MCP) for task routing
- RL Feedback Loop for quality improvement
- LangGraph automation pipeline
- BHIV integration with WebSocket streaming

## Project Structure

```
src/
├── db/              # MongoDB connection and models
├── services/        # Uniguru and external API services
├── agents/          # Agent Registry and task routing
├── pipeline/        # LangGraph-style automation pipeline
├── feedback/        # RL feedback loop implementation
├── routes/          # Express API routes
├── models/          # Data models and schemas
└── validation/      # Sample validation tests

config/             # Configuration files
tests/              # Test suite
```

## Setup Instructions

### 1. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your MongoDB Atlas URI and Uniguru API key
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Initialize Database
```bash
npm run seed-db
```

### 4. Validate with Sample News
```bash
npm run validate-samples
```

### 5. Run Development Server
```bash
npm run dev
```

## API Endpoints

- `POST /api/news` - Submit raw news item
- `GET /api/news/:id` - Get news by status (raw/verified/published)
- `POST /api/agents/register` - Register new agent
- `POST /api/agents/task` - Submit task to agent
- `GET /api/feedback/metrics` - Get RL feedback metrics
- `WS ws://localhost:3001` - WebSocket for streaming

## Pilot Readiness

### Channels × Avatars
- Channels: ttv, vaani, other
- Avatars: avatarA, avatarB, avatarC

### Run Pilot
```bash
node src/validation/run-pilot.js
```
Outputs JSON with latency, reward, success, iterations for all combinations.

### Integration Diagram
```
           +---------------------------+
           |  Chandragupta Frontend   |
           |  (Next.js / App Router)  |
           +------------+--------------+
                        |
                        v
         +--------------+---------------+
         |        Noopur News AI        |
         |  Express + WebSocket (3000/1)|
         |  Agents + RL + LangGraph     |
         +---+-----------+-----------+--+
             |           |           |
             v           v           v
        Fetch         Verify       Script
             \           |           /
              \          v          /
               +------ Feedback ----+
                         |
                         v
                +--------+--------+
                |       BHIV      |
                |  TTV  |  Vaani  |
                +--------+--------+
                        |
                        v
                 WebSocket Broadcast
```

## Phases

### Phase 1: MongoDB Atlas + Uniguru Integration
- News schema with pipeline stages
- Uniguru endpoint wrappers
- Sample validation with 5 news items

### Phase 2: Agent Registry (Day 1-2)
- Fetch, Filter, Verify, Script, RLFeedback agents
- Async task routing
- BHIV Core integration

### Phase 3: RL Feedback Loop (Day 2-3)
- Reward evaluation (tone + engagement)
- Auto-rerouting for re-summarization
- Metrics logging

### Phase 4: LangGraph Automator (Day 3-4)
- Self-correcting pipeline
- Adaptive reprocessing
- 10-story validation

### Phase 5: BHIV Integration (Day 4-5)
- TTV/Vaani endpoint integration
- WebSocket streaming
- End-to-end testing

## Production Notes
- Optimized indexes: publishedAt, tags, processingLog.stage; agentRole; rewardScore, latency
- Seeya-compatible JSON: /api/bhiv/process, /api/bhiv/stream, /api/bhiv/core/sync
- Threshold tuning: `POST /api/feedback/threshold` with `{ "threshold": 0.6 }`
