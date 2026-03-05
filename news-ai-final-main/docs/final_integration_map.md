# Final Integration Map (v2)

## System Connections
- Noopur backend
  - FastAPI microservice for Uniguru: classify/sentiment/summarize, background enrichment, MongoDB storage ([main.py](file:///c:/Users/black/OneDrive/Desktop/news%20ai%20final/Noopur%20News%20ai/fastapi_microservices/main.py))
  - Node/Express pipeline: agents registry, RL feedback loop, LangGraph pipeline, BHIV integration, WebSocket broadcasting ([index.js](file:///c:/Users/black/OneDrive/Desktop/news%20ai%20final/Noopur%20News%20ai/src/index.js))
- Seeya orchestrator
  - FastAPI wrapper endpoints: /fetch → /process → /voice → /feedback with JWT, mounts UI and serves generated media ([server/app.py](file:///c:/Users/black/OneDrive/Desktop/news%20ai%20final/Seeya%20News%20ai/server/app.py))
- Sankalp Insight Node
  - Unified Tools FastAPI backend: /api/unified-news-workflow and related tools for scraping, vetting, summarization, prompts, video search ([main.py](file:///c:/Users/black/OneDrive/Desktop/news%20ai%20final/Sankalp%20news%20ai/unified_tools_backend/main.py))
- Chandragupta frontend
  - Next.js app targeting Noopur base URL, health-checks /health, adds secure headers and optional JWT. Uses mock fallback in dev ([api.js](file:///c:/Users/black/OneDrive/Desktop/news%20ai%20final/chandragupta%20frontend/blackhole-frontend/services/api.js))

## Diagram
- Integration_map_v2.png shows: Inputs → Agents → RL loops → Scripts → Voice → UI preview → Final export
- Source: [integration_map_v2.mmd](file:///c:/Users/black/OneDrive/Desktop/news%20ai%20final/Noopur%20News%20ai/docs/integration_map_v2.mmd)
- Image: [integration_map_v2.png](file:///c:/Users/black/OneDrive/Desktop/news%20ai%20final/Noopur%20News%20ai/docs/integration_map_v2.png)

## Data Flow Alignment
- Inputs
  - Noopur: /api/news creates raw item and starts enrichment, or pipeline consumes verified items
  - Seeya: /fetch builds items list and preview for UI
  - Sankalp: /api/scrape and unified workflow ingest from URL
- Agents
  - Noopur: registry roles fetch, verify, script
  - Seeya: runs filter and scripts stages for UI preview
  - Sankalp: tool-specific agents via unified endpoints
- RL Loop
  - Noopur: RLFeedbackLoop computes rewardScore, triggers corrections, sets threshold
  - Seeya: user feedback via /feedback flows to DB and rate-limited endpoints
- Scripts
  - Noopur: script stage generates narrative; enrichment adds classification/sentiment/summary
  - Seeya: /process returns counts and script previews
- Voice
  - Noopur: BHIV integration “vaani” publishes summaries/entities and tone
  - Seeya: /voice generates voice items and preview
- UI Preview
  - Chandragupta frontend uses API service to display pipeline status and results
- Final Export
  - Noopur: BHIV stream to ttv/vaani and core sync exposes Seeya-compatible articles

## JSON Compatibility Validation
- Seeya /process response (representative):
  ```json
  {
    "status": "ok",
    "counts": { "filtered": 12, "scripts": 8 },
    "preview": [
      {
        "title": "Story title",
        "lang": "en",
        "audience": "general",
        "tone": "neutral",
        "variants": [/* ... */],
        "metadata": {/* ... */}
      }
    ],
    "files": { "filtered": "path.json", "scripts": "path.json" }
  }
  ```
- Noopur /api/bhiv/process response (key parts) and mapping:
  ```json
  {
    "success": true,
    "pipelineResult": {
      "finalRewardScore": 0.72,
      "iterations": 2,
      "processingTime": 1450,
      "pipelineResult": {
        "fetch": {/* stage output */},
        "verify": {/* stage output */},
        "script": {/* stage output */}
      }
    },
    "seeya_compat": {
      "id": "mongo_id",
      "title": "Story title",
      "source_name": "noopur",
      "source_url": "",
      "thumbnail_url": "",
      "category": "general",
      "published_at": "2026-02-05T00:00:00Z",
      "relevance_score": 0.72,
      "processing_status": "published",
      "processing_progress": 3,
      "group_key": null
    }
  }
  ```
- Compatibility notes
  - Preview array in Seeya maps to Noopur’s script stage output. For UI parity, extract `pipelineResult.script` and emit `preview[]` with keys: title, lang, audience, tone, variants, metadata.
  - Counts.filtered/scripts derive from lengths of `pipelineResult.verify` and `pipelineResult.script` outputs if stored; otherwise 0.
  - When streaming, Noopur already returns `seeya_compat.articles[]` and `meta` that match Seeya’s feed expectations.
  - Conclusion: Noopur can produce a Seeya-compatible payload without schema changes by shaping the existing stage outputs into Seeya’s preview/counts structure.

## Regenerating the Diagram
- Requires Mermaid CLI
  - Install globally: `npm i -g @mermaid-js/mermaid-cli`
  - Generate: `npx mmdc -i docs/integration_map_v2.mmd -o docs/integration_map_v2.png`

## Unified Endpoint
- Final endpoint: `POST /v1/run_pipeline`
- Triggers: Fetch → Filter → Verify → Script → RL correction → BHIV push → Sankalp audio
- Returns: counts, preview[], pipeline metadata, seeya_compat, audio info
- Schemas: tone (neutral/informative/urgent/optimistic/serious/excited), language (ISO code), avatar_ready (bool)
- Fallback: If Uniguru is down, scraping/summarization via unified tools, template prompts for audio

## Deployment Considerations
- Health endpoints
  - Noopur FastAPI: `/health`
  - Noopur Node: `/health`
  - Sankalp/Akash unified: `/health`
- CORS
  - Allow `http://localhost:3000` and deployed frontend origin
- Security headers
  - Frontend sends `X-Client-Nonce`, `X-Signature`, `X-Timestamp`, optional `Authorization` JWT; backend should accept gracefully
