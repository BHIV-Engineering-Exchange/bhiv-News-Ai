# Deterministic Ingestion Pipeline: Final Execution Proof

**Project:** News AI - Truth Intelligence Layer
**Verified:** 2026-04-04
**Status:** COMPLETE - deterministic ingestion flow validated

## Input Sample

```json
{
  "source_url": "https://example.com/news/weather",
  "raw_content": "IMD predicts normal monsoon in 2026. Rainfall expected to be normal.",
  "registry_reference_id": "REG_WEATHER_2026_03",
  "location": "India",
  "sources": [
    {
      "source_id": "imd",
      "is_institutional": true,
      "authority_score": 0.92
    }
  ]
}
```

## Pipeline Flow

1. Generate `source_hash` from raw content before parsing.
2. Validate the canonical ingestion schema strictly.
3. Normalize geo text into a deterministic geo object or `null`.
4. Classify truth level using the existing deterministic truth classifier.
5. Detect conflict state using the existing deterministic conflict detector.
6. Generate `event_id` as `SHA-256(source_hash + registry_reference_id)`.
7. Emit the final standardized output only.

## Verified Output

```json
{
  "event_id": "a990f84b02a90f33aae31b0cf80faa14811f6171b8a984f4fdf774c0f3239984",
  "source_hash": "86cbfde918020c1cde0dfd7e5591dd02f99a5519fe787f04043c4897d1b88880",
  "truth_level": 3,
  "conflict_flag": false,
  "geo_normalized": {
    "country_code": "IN",
    "region": null,
    "lat": 20.5937,
    "lon": 78.9629,
    "confidence": 0.8
  },
  "registry_reference_id": "REG_WEATHER_2026_03"
}
```

## Replay Results

The backend replay suite was executed with 3 replays for the same input.

- `event_id` identical across all runs: pass
- `truth_level` identical across all runs: pass
- `conflict_flag` identical across all runs: pass

The batch replay test also passed with 5 inputs across 3 runs, producing identical outputs on each run.

## Monitoring Snapshot

A deterministic monitor report was generated after two successful ingestions.

- ingestion success rate: 100%
- schema failures: 0
- classification failures: 0
- geo resolution rate: 100%
- health status: HEALTHY
