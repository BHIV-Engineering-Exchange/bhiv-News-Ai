# Truth Classification Rules: Samachar Ingestion Layer

This document defines the deterministic rules for assigning `truth_level` signals to news ingestion events. 

## Classification Hierarchy

| Level | Name | Detection Rule | Description |
| :--- | :--- | :--- | :--- |
| **0** | **Unverified Claim** | `len(unique_sources) == 0` | No valid source hashes or signals detected for the event. |
| **1** | **Single-Source Reported** | `len(unique_sources) == 1` | Exactly one unique source hash or signal detected. |
| **2** | **Multi-Source Corroborated** | `len(unique_sources) >= 2` | Two or more unique source hashes corroborate the claim. |
| **3** | **Institutional / Authority** | `is_institutional: True` or `authority_score >= 0.8` | Signal from an official entity, verified news agency, or primary reporter. |
| **4** | **Direct Documented Evidence** | `primary_evidence: True` or `document_hash: PRESENT` | Source includes direct primary evidence (e.g., PDF, scan, official transcript hash). |

## Deterministic Priorities

Classification follows a strict top-down priority (highest level match wins):

1. **Direct Documented Evidence (4)**
2. **Institutional / Authority (3)**
3. **Multi-Source Corroborated (2)**
4. **Single-Source Reported (1)**
5. **Unverified Claim (0)**

## Key Signal Definitions

- `source_hash`: Canonical source identifier provided by Noopur's hashing layer.
- `is_institutional`: Boolean flag for verified official entities.
- `authority_score`: Normalized value [0-1] for institutional reliability.
- `primary_evidence`: Boolean flag for direct, first-party documented evidence.
- `document_hash`: Unique hash of a primary source document (e.g., official release).

No probabilistic inference, interpretative AI judgement, or summarization is applied during classification.
