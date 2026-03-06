# Determinism Validation Report

Purpose

This file documents how deterministic replay validation is performed for
Samachar alignment. The repository includes a small test harness that
verifies repeated classification of the same `source`+`content` yields the
same `event_id` and `truth_level`.

How to run

From the repository root run:

```powershell
pytest -q
```

What to check

- `event_id` must be stable across repeated runs for the same `source`+`content`.
- `truth_level` must be identical across repeated runs for the same inputs.
- The test `tests/test_truth_and_determinism.py` exercises both properties.

If any of the checks fail, the cause will typically be:

- Use of non-deterministic data (timestamps, random numbers) in the
  classification input before `event_id` is computed.
- Use of ephemeral signals or external service calls during classification.

Remediation

- Ensure `event_id` is computed only from stable fields (source, raw content).
- Make rule changes explicit in `docs/truth_classification_rules.md` and
  bump the module version or add a changelog entry so past results can be
  migrated or re-evaluated.
