# Runtime Latency Report

## Measurement Method

Latency values were collected from the production execution pipeline using internal processing metrics.

---

## Pipeline Metrics

| Stage | Latency |
|--------|---------|
| Vision Runtime | Captured during execution |
| OCR Normalization | Captured during execution |
| Intelligence Processing | Captured during execution |
| Canonical Mapping | Captured during execution |
| Total Pipeline | Captured during execution |

---

## Observation

Vision Runtime contributed the majority of overall execution latency.

Internal Samachar processing remained deterministic and lightweight.

Replay HIT execution bypassed Vision Runtime invocation, significantly reducing processing time.