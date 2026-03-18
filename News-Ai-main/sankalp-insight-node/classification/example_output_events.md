# Example Output Events: Samachar Truth Engine

This document provides examples of deterministic truth-tagged events emitted by the Samachar Truth Engine.

## Example 1: Institutional Verified Report (Level 3)
```json
{
  "event_id": "b1e9865b4455b69f3f13985e2ad239d9292fb64c13faed037ce088f509142f29",
  "source_hash": "SOURCE_HASH_001",
  "registry_reference_id": "REGISTRY_ID_001",
  "timestamp": "2026-03-18T10:00:00Z",
  "truth_level": 3,
  "conflict_flag": false,
  "status": "verified"
}
```

## Example 2: Corroborated Multi-Source Report (Level 2)
```json
{
  "event_id": "42c38d9f18a221f5e27306381d1ed1d829e8270ea3dead53b0724e337d05ed",
  "source_hash": "SOURCE_HASH_002",
  "registry_reference_id": "REGISTRY_ID_002",
  "timestamp": "2026-03-18T10:05:00Z",
  "truth_level": 2,
  "conflict_flag": false,
  "corroborating_sources": 3
}
```

## Example 3: Contradictory Structural Flag (Conflict Detected)
```json
{
  "event_id": "98a12c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1",
  "source_hash": "SOURCE_HASH_003",
  "registry_reference_id": "REGISTRY_ID_001",
  "timestamp": "2026-03-18T10:10:00Z",
  "truth_level": 1,
  "conflict_flag": true,
  "status": "closed"
}
```
*(Note: Conflict detected because `REGISTRY_ID_001` already had `status: verified` in Example 1.)*
