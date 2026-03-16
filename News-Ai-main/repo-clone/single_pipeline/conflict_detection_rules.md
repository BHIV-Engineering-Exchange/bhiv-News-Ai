# Conflict Detection Rules: Samachar Truth Tagging

This document defines the deterministic rules for flagging structural contradictions in the Samachar truth layer based on `registry_reference_id`.

## Detection Strategy

Conflicts are evaluated only between events sharing the same canonical `registry_reference_id`. The detection logic is deterministic and non-interpretive.

| Contradiction Type | Rule | Description |
| :--- | :--- | :--- |
| **Factual / Categorical** | `count(unique(status|outcome|state)) > 1` | Multiple distinct statuses or outcomes reported for the same registry entry. |
| **Opposing Claims** | `count(unique(is_active|is_verified|is_complete)) > 1` | Conflicting boolean states (e.g., reporting both `is_active: True` and `False`). |
| **Numeric Incompatibility** | `count(unique(amount|count|score|value)) > 1` | Differing numeric measurements for the same reference identifier. |
| **Timeline Incompatibility** | `non_sequential_updates` | Structurally impossible state changes or overlapping timestamps for identical events. |

## Discipline: Flag, Not Resolve

*   **Conflict Detected**: `conflict_flag = true`
*   **Conflict Not Detected**: `conflict_flag = false`

**Crucial Discipline**: The ingestion layer must only signal the presence of a contradiction. It is strictly forbidden to merge, collapse, or resolve these conflicts at this stage. The structural ambiguity must be preserved for downstream governance-neutral systems.

## Monitored Fields

The following fields are monitored for structural convergence:
- `status`, `outcome`, `state`
- `is_active`, `is_verified`, `is_complete`, `is_truthful`
- `amount`, `count`, `score`, `value`, `price`, `quantity`
- `timestamp`, `date` (for sequence integrity)

Detection is purely signal-based; no probabilistic AI inference or interpretive judgment is applied.
