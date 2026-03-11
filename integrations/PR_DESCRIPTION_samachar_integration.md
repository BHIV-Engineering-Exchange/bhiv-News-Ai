Title: Add deterministic truth classifier and Samachar integration wrapper

Summary:
- Adds a deterministic `truth_classifier` module implementing Levels 0-4.
- Adds a `conflict_detector` module that flags contradictions by `registry_reference_id`.
- Adds `integrations/samachar_integration.py` which emits truth signals without
  mutating original events.
- Documentation: `truth_decision_tree.md`, `determinism_validation_report.md`,
  and `integrations/SAMACHAR_INTEGRATION.md` with wiring examples.
- Tests: `tests/test_truth_and_conflict.py` (targeted tests pass locally).

Contracts & Constraints:
- No schema changes, no new fields added to original events.
- Deterministic, rule-based logic only. No probabilistic inference.
- Conflict detection does not resolve or overwrite prior data.

Files changed / added:
- truth_classifier.py
- conflict_detector.py
- integrations/samachar_integration.py
- integrations/SAMACHAR_INTEGRATION.md
- truth_decision_tree.md
- determinism_validation_report.md
- tests/test_truth_and_conflict.py

Testing instructions:
1. Run targeted tests only:

```bash
PYTHONPATH=. pytest -q tests/test_truth_and_conflict.py
```

2. Integration usage (example) is in `integrations/SAMACHAR_INTEGRATION.md`.

Notes for reviewers:
- Reviewers should verify the rule ordering in `truth_decision_tree.md`.
- Verify that `emit_truth_signals` does not mutate inputs and that conflict
  grouping uses `registry_reference_id` deterministically.

Tag: truth_classifier_v1
