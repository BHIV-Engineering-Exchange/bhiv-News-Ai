# Classification Rules: Samachar Truth Tagging

This document defines the deterministic, signal-based truth classification levels for the Samachar truth ingestion layer.

## Levels Overview

| Level | Name | Signal Requirements | Description |
| :--- | :--- | :--- | :--- |
| **0** | **Unverified Claim** | `len(sources) == 0` | No valid sources or signals provided for ingestion. |
| **1** | **Single-Source Reported** | `len(unique_source_hashes) == 1` | Exactly one unique source hash or signal detected. |
| **2** | **Multi-Source Corroborated** | `len(unique_source_hashes) >= 2` | Two or more unique source hashes/IDs corroborate the claim. |
| **3** | **Institutional / Authority** | `is_institutional: True` or `authority_score >= 0.8` | Source is marked as an institutional or official primary authority. |
| **4** | **Direct Documented Evidence** | `primary_evidence: True` or `document_hash: PRESENT` | Source includes direct primary evidence (e.g., PDF, scan, official transcript). |

## Deterministic Priorities

Classification follows a top-down priority (highest level match wins):

1.  **Direct Documented Evidence (4)**
2.  **Institutional / Authority (3)**
3.  **Multi-Source Corroborated (2)**
4.  **Single-Source Reported (1)**
5.  **Unverified Claim (0)**

## Signal Definitions

*   `source_hash`: Canonical source identifier (provided by Noopur's hashing layer).
*   `is_institutional`: Boolean flag indicating if the source represents an official entity or verified primary reporter.
*   `authority_score`: Normalized value [0-1] for institutional reliability.
*   `primary_evidence`: Boolean flag for direct, first-party documented evidence.
*   `document_hash`: Unique hash of a primary source document (e.g., official release, contract, transcript).

No probabilistic inference, heuristic optimism, or summarization is applied during classification.
