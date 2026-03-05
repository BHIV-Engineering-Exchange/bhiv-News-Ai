# Truth Decision Tree (Starter)

This document describes the deterministic decision tree used by the
starter `truth_classifier.py`. The goal is transparency: each rule is
deterministic, easy to test, and readable by non-developers.

Decision flow:

1. Fabricated (truth_level = 0)
   - If the headline or body contains tokens like "fabricat", "hoax",
     "made up", or "false".

2. Satire (truth_level = 1)
   - If tokens "satire", "parody", or "spoof" appear.

3. Verified (truth_level = 4)
   - If `source` domain matches a trusted list (e.g. `trustednews.com`),
     OR if an explicit `confidence` field is present and >= 0.90.

4. Needs verification (truth_level = 2)
   - If language uses hedging or attribution such as "alleged",
     "reportedly", "claims", or "according to".

5. Plausible / Unverified (truth_level = 3)
   - Default fallback when none of the above rules apply.

Examples:
- {"headline": "This story is a hoax"} -> 0
- {"headline": "Official notice from reliable.org", "source": "reliable.org"} -> 4
- {"headline": "Local report reportedly says..."} -> 2

Notes:
- This decision tree is intentionally conservative and heuristic-based.
- It is a reference implementation for transparency and testing, not
  a production-grade classifier. Use it to generate deterministic
  test cases and to document expected behavior.
