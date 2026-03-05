# Demo Notes (Canonical)

- What the system does
  - Ingests a news item, enriches via Uniguru (classification, sentiment, summary)
  - Runs agent pipeline and RL evaluation; publishes when reward ≥ threshold
  - Exposes compatible payloads for frontend and orchestrator; supports audio prompt via Sankalp

- If latency happens
  - Expected: brief pauses during enrichment and pipeline stages
  - Say: “The pipeline is verifying and scripting; RL is ensuring quality. If it takes more than a few seconds, results still publish and the UI will update.”
  - Deterministic mode available (RL_DETERMINISTIC=true) to stabilize behavior during demos

- Expected vs unexpected
  - Expected: preview list appears; pipeline statuses progress; audio may be “not yet generated”
  - Unexpected: 5xx errors or missing required fields — surfaces as error JSON with clear codes (e.g., create_news_failed, bhiv_process_failed)

- Canonical demo
  - URL: https://www.bbc.com/news/world-12345678
  - Path: POST /v1/run_pipeline with { url, language: "en", tone: "neutral", avatar_ready: false }
  - Golden payload (shape):
    {
      "success": true,
      "timestamp": "2026-02-05T00:00:00Z",
      "newsItemId": "507f1f77bcf86cd799439011",
      "counts": { "filtered": 1, "scripts": 3 },
      "preview": [
        { "title": "Story title", "lang": "en", "audience": "general", "tone": "neutral", "variants": [], "metadata": {} }
      ],
      "pipeline": {
        "uniguru_ok": true,
        "rl_rerun_triggered": false
      },
      "seeya_compat": null,
      "audio": { "status": "none" }
    }

- Talking points
  - Contract and schemas are frozen for demo (demo-stable-v1)
  - Health and release tag: GET /api/system/info → releaseTag demo-stable-v1
  - Header validation for orchestrator: GET /auth/validate with HMAC headers
