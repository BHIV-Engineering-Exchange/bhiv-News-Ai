# REVIEW PACKET - Deterministic Intelligence Retrieval Engine

Project: Samachar Queryable Intelligence Conversion  
Assigned: 2026-03-29  
Due: 2026-03-30  
Delivery Date: 2026-04-04

## 1) Entry Point

Primary entry point: [intelligence_query/query_engine.py](../intelligence_query/query_engine.py)

Main callable for integration:
- run_query(registry, query, base_dir)

Batch fixture generation:
- run_queries_file(registry, queries_path, output_path, base_dir)
- Vinayak regression entrypoint: [intelligence_query/validate_query_outputs.py](../intelligence_query/validate_query_outputs.py)

## 2) Three Core Files

1. [intelligence_query/query_engine.py](../intelligence_query/query_engine.py)
- Data load: load_intel_events, load_signals
- Join: event_id-based join with strict no-partial-record output
- Filtering: geo, start_time/end_time, min_truth_level, signal_type, conflict_flag
- Routing: exact Samachar/Guptachar rule
- Response builder: query, results, signals, summary, route, tts_text

2. [intelligence_query/fixtures/sample_queries.json](../intelligence_query/fixtures/sample_queries.json)
- High truth case
- Conflict case
- Low truth case

3. [intelligence_query/fixtures/sample_outputs.json](../intelligence_query/fixtures/sample_outputs.json)
- Deterministic output generated from sample queries
- Stable ordering and stable content

Supporting dataset files used for deterministic test execution:
- [intelligence_query/data/demo_intel_events.json](../intelligence_query/data/demo_intel_events.json)
- [intelligence_query/data/demo_signals.json](../intelligence_query/data/demo_signals.json)

## 3) Execution Flow

1. Load registry datasets:
- <registry>_intel_events.json
- <registry>_signals.json

2. Join on event_id:
- Keep only complete records containing:
  - event_id
  - geo
  - timestamp
  - truth_level
  - conflict_flag
  - signal_type
  - is_sensitive

3. Apply filters (if present):
- geo
- start_time
- end_time
- min_truth_level
- signal_type
- conflict_flag

4. Compute routing per result:
- If is_sensitive == true OR truth_level <= 1 => guptachar
- Else => samachar

5. Compute overall route:
- If any result is guptachar => guptachar
- Else => samachar

6. Build deterministic response:
- query
- results
- signals
- summary
- route
- tts_text

## 4) Real Output JSON (Excerpt)

From [intelligence_query/fixtures/sample_outputs.json](../intelligence_query/fixtures/sample_outputs.json), low truth case:

```json
{
  "query": {
    "query_name": "low_truth_case",
    "geo": "Delhi",
    "start_time": "2026-03-29T00:00:00Z",
    "end_time": "2026-03-29T23:59:59Z",
    "min_truth_level": 0,
    "signal_type": "low",
    "conflict_flag": false
  },
  "results": [
    {
      "event_id": "evt_demo_003",
      "geo": "Delhi",
      "timestamp": "2026-03-29T12:00:00Z",
      "truth_level": 1,
      "conflict_flag": false,
      "signal_type": "low",
      "is_sensitive": false,
      "route": "guptachar"
    }
  ],
  "route": "guptachar"
}
```

## 5) Failure Cases Covered

1. Missing dataset file
- Behavior: returns empty list, no crash

2. Missing filter in query
- Behavior: filter ignored, no crash

3. Missing fields in source records
- Behavior: partial joined record dropped

4. Non-boolean conflict input
- Behavior: normalized safely or ignored in filter match path

5. No matching records
- Behavior: deterministic empty response with summary text

## 6) Determinism Proof

The same input file was executed twice using run_queries_file and output hashes matched exactly:

- SHA-256 run 1: 409d36a3617ad3677cb3a7c4b97952bd19bde6b6cb2773381720c0dcba5bcb45
- SHA-256 run 2: 409d36a3617ad3677cb3a7c4b97952bd19bde6b6cb2773381720c0dcba5bcb45
- Result: identical outputs (True)

## 7) Acceptance Criteria Mapping

- Query returns filtered results correctly: PASS
- Signals correctly attached to events: PASS
- Routing logic correct (samachar / guptachar): PASS
- Response format consistent: PASS
- No crashes on edge cases: PASS
- Deterministic output verified: PASS
