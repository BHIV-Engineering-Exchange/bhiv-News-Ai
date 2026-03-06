# Truth Classification Rules

This document describes the deterministic rule-set implemented in
`sankalp-insight-node/classification/truth_classifier.py`.

Rules (applied in order):

1. If content contains any of: `official`, `announced`, `confirmed`, `statement` → truth_level = 4 (highest confidence).
2. Else if content contains `reported`, `sources say`, `according to` → truth_level = 3 (sourced reporting).
3. Else if content contains `unverified`, `alleged`, `may have` → truth_level = 2 (unverified/ambiguous).
4. Else if content contains `rumor`, `rumours`, `hearsay` → truth_level = 1 (rumor-like).
5. Else if content contains `satire`, `not true`, `fake news`, `hoax` → truth_level = 0 (false/satire).
6. Fallback heuristics:
   - Short content (less than 6 words) → truth_level = 1.
   - Otherwise → truth_level = 2.

Deterministic Event ID

- `event_id` is the SHA256 hex digest of the string `"{source}|{content}"`.
- This ensures the same `source`+`content` always yields the same `event_id`.

Design notes

- The rules are intentionally simple to maintain transparency and deterministic
  behavior. They are suitable as a canonical baseline; teams should extend
  them only with documented, version-controlled changes.
