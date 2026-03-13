# Insight Narrator Node (news-ai)

## Setup

- Python 3.11+
- Windows: `powershell -ExecutionPolicy Bypass -File scripts/setup.ps1`
- Env (optional):
  - `UNIGURU_SUMMARY_URL`, `UNIGURU_API_KEY`
  - `VAANI_TTS_URL`, `VAANI_API_KEY`
  - `RL_WEIGHTS_JSON`
  - `AUTOMATOR_PRIORITY_THRESHOLD`, `AUTOMATOR_REWARD_THRESHOLD`

## Pipeline

- Ingest → Summarize → Sentiment → Synthesize → Rank → Export
- Runners:
  - `python scripts/run_ingest.py`
  - `python scripts/format_metadata.py`
  - `python scripts/generate_audio.py --avatar <name> --voice <id>`
  - `python scripts/smart_feed.py`
  - `python scripts/run_pipeline.py` (end-to-end)

## Endpoints

- `POST /feedback`: `{ id, item, signals }`
- `POST /requeue`: `{ id }`
- Server: `python scripts/api_server.py`

## JSON Schema (integration)

- Item fields:
  - `id`: string
  - `script`: string (use `summary_medium`)
  - `tone`: string
  - `language`: string
  - `audio_path`: string
  - `priority_score`: number
  - `trend_score`: number

## Exports

- `exports/weekly_report.csv`
- `exports/weekly_report.json`
- `exports/sample_integration.json`

## Notes

- Offline-safe; falls back when APIs are not configured.
- Timezone-normalized to UTC for ranking and trend.