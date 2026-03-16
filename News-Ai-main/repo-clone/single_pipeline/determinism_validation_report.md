# Determinism Validation Report: Samachar Truth Ingestion Layer

This report confirms the deterministic, replayable nature of the truth classification and conflict detection modules implemented for Samachar.

## Validation Summary

*   **Test Environment**: News AI Unified Ingestion (Local)
*   **Timestamp**: 2026-03-13
*   **Modules Tested**: `truth_classifier.py`, `conflict_detector.py`
*   **Result**: **PASSED**

## Test Case 1: Identical Source Ingestion (Replayability)

Verifies that ingesting the same source metadata twice produces identical event IDs and truth tags.

### Input Source
```json
{
  "source_hash": "HASH_ABC_123",
  "registry_reference_id": "REG_999",
  "timestamp": "2026-03-13T12:00:00Z",
  "is_institutional": true,
  "status": "verified",
  "amount": 5000
}
```

### Output Comparison
| Field | Run 1 | Run 2 (Replay) | Match |
| :--- | :--- | :--- | :--- |
| `event_id` | `91728285...` | `91728285...` | ✅ |
| `truth_level` | 3 | 3 | ✅ |
| `conflict_flag` | false | false | ✅ |
| `registry_id` | REG_999 | REG_999 | ✅ |

## Test Case 2: Structural Contradiction (Conflict Detection)

Verifies that incompatible numeric values for the same `registry_reference_id` trigger the `conflict_flag`.

### Conflict Input
*   **Event A**: `amount: 5000`
*   **Event B**: `amount: 10000`
*   **Registry ID**: `REG_999`

### Detection Result
*   **`conflict_flag`**: `true` ✅
*   **Discipline Check**: Conflict flagged without resolving or collapsing the differing values.

## Determinism Confirmation

1.  **No Randomness**: No `random` seeds or non-deterministic libraries are used.
2.  **Explicit Rules**: All logic is based on explicit value comparisons and metadata presence.
3.  **Order Independence**: Truth classification is independent of source processing order.
4.  **Signal-Based**: Levels are assigned purely based on provided ingestion signals.

This deterministic behavior is critical for maintaining structural integrity and preventing silent truth mutation in downstream systems.
