# Determinism Validation Report

Objective: Verify identical inputs produce identical `(truth_level, conflict_flag)`
outputs from `truth_classifier` and `conflict_detector`.

Method:
- Unit tests provide fixed inputs and assert stable outputs across repeated
  invocations.
- No randomness or time-dependent logic is used.

Results:
- Unit tests included in `tests/test_truth_and_conflict.py` pass locally.
- Manual inspection confirms functions are pure and deterministic.

Tag: truth_classifier_v1
