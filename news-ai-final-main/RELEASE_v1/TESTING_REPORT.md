# Testing Report

- Scope
  - Frontend-backend linking
  - Live feed, pipeline viewer, voice preview
  - Feedback recording and RL evaluation
- Tools
  - Local manual tests via curl and browser
  - Sankalp run_full_test.py for feed/feedback sanity
- Results
  - Health: OK
  - Live feed: OK (published list)
  - Pipeline viewer: OK (polling /api/processed/:id)
  - Voice preview: OK when audioUrl present; graceful fallback else
  - Feedback: OK; counts updated on item.feedback
- Artifacts
  - logs/rl/rl_metrics.jsonl (runtime)
  - logs/rl/rl_summary.json (benchmark)
