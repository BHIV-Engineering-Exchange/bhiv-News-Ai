# Truth Decision Tree

This document records the explicit, deterministic decision tree used by
`truth_classifier.classify_claim`.

Rules (evaluated top-to-bottom):

1. If any evidence item has `evidence_type: "direct"` -> truth_level = 4
2. Else if any evidence item has `evidence_type: "institutional"` -> truth_level = 3
3. Else if distinct sources count >= 2 -> truth_level = 2
4. Else if number of `evidence_type: "report"` items >= 2 -> truth_level = 2
5. Else if distinct sources == 1 OR number of `report` items == 1 -> truth_level = 1
6. Else -> truth_level = 0

Notes:
- Deterministic: the output depends only on explicit fields `sources` and
  `evidence` present in the input dict.
- No probabilistic inference, no time-based thresholds, and no hidden
  randomness.
- The classifier does not modify input events or schema.
