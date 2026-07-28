# Replay Validation

## Replay MISS

First execution generated:

- new fingerprint
- Vision Runtime invocation
- ReplayStore persistence

---

## Replay HIT

Second execution using the identical image:

- identical fingerprint
- ReplayStore retrieval
- Vision Runtime skipped
- identical canonical intelligence returned

---

## Result

Replay behaviour is deterministic and consistent across repeated executions.