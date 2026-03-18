# Conflict Detection Rules: Samachar Ingestion Layer

This document defines the rules for deterministic, non-resolving conflict detection based on `registry_reference_id`.

## Detection Strategy

The Samachar truth ingestion layer evaluates contradictions between events sharing the same canonical `registry_reference_id`.

| Contradiction Type | Detection Signal | Description |
| :--- | :--- | :--- |
| **Factual Contradiction** | `len(unique(status)) > 1` | Differing 'status', 'outcome', or 'verified' values for the same reference. |
| **Opposing Claim** | `len(unique(is_active)) > 1` | Conflicting values for boolean attributes (e.g., 'is_active', 'is_verified', 'is_complete'). |
| **Incompatible Numeric** | `len(unique(amount)) > 1` | Differing values for 'amount', 'count', or 'score' for the same reference. |
| **Timeline Incompatibility** | `non_sequential_events` | Overlapping or non-sequential 'timestamp' or 'date' sequences for the same claim. |

## Flagging Protocol

- **Conflict Detected**: `conflict_flag = true`
- **Conflict Not Detected**: `conflict_flag = false`

## Core Disciplines

1. **Flag, Not Resolve**: Conflict is only flagged to signal ambiguity. The ingestion layer must **not** merge, collapse, or resolve contradictions.
2. **Preserve Ambiguity**: Contradictions must remain preserved in the canonical truth stream for downstream governance-neutral systems.
3. **Registry Alignment**: Conflict detection is only performed between events sharing the same canonical `registry_reference_id` (provided by Chandragupta's registry mapping layer).
4. **No Heuristic Inference**: Deterministic value comparison only. No probabilistic inference or interpretation is allowed.

## Monitored Attributes

The following attributes are monitored for structural contradictions:
- `status`
- `outcome`
- `amount`
- `count`
- `score`
- `value`
- `is_active`
- `is_verified`
- `is_complete`
- `is_truthful`
- `timestamp` / `date` (for sequence validation)
