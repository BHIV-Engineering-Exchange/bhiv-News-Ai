# Samachar Integration Instructions

This document explains how to integrate the `integrations/samachar_integration.py`
wrapper into the Samachar ingestion layer without modifying event schemas.

Goals:
- Do not mutate incoming events.
- Do not add fields to original events.
- Emit separate truth signals that downstream systems (Seeya, Noopur, Chandragupta)
  can consume.
- Maintain deterministic, replayable behavior.

Example (synchronous call within ingestion worker):

```python
from integrations.samachar_integration import emit_truth_signal_for_event

def handle_ingested_event(event):
    # event is the original dict from Samachar (do NOT modify it)
    signal = emit_truth_signal_for_event(event)
    # persist or emit the signal to the event bus / DB / log
    # e.g., message_bus.publish('truth_signals', signal)
    log.info('truth_signal_emitted', registry_reference_id=signal.get('registry_reference_id'), truth_level=signal['truth_level'], conflict_flag=signal['conflict_flag'])

    # continue normal ingestion workflow (no changes to `event`)

```

Batch example (recommended when processing batches):

```python
from integrations.samachar_integration import emit_truth_signals

signals = emit_truth_signals(batch_of_events)
# persist/emit signals in same order as input events to preserve replayability
for s in signals:
    message_bus.publish('truth_signals', s)
```

Notes:
- `emit_truth_signals` uses only `sources`, `evidence`, and `registry_reference_id`
  fields where present. It is deterministic and pure.
- Conflict detection groups events by `registry_reference_id`. If your ingestion
  worker de-duplicates or batches by that id, emit signals per batch to ensure
  consistent conflict flags.
- Do NOT use signals to overwrite existing stored events. Use them as separate
  observational metadata consumed by Seeya (Contract Enforcement) or downstream
  analysts.
