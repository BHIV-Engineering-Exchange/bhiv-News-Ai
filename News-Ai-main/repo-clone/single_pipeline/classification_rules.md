# Classification Rules: Samachar Truth Tagging

This document defines the deterministic, rule-based truth classification levels for the Samachar truth ingestion layer.

## Levels Overview

| Level | Name | Requirements | Description |
| :--- | :--- | :--- | :--- |
| **0** | **Unverified Claim** | `len(unique_sources) == 0` | No valid source identifiers or corroborating signals detected. |
| **1** | **Single-Source Reported** | `len(unique_sources) == 1` | Exactly one unique source hash or ID reported the claim. |
| **2** | **Multi-Source Corroborated** | `len(unique_sources) >= 2` | Two or more unique source identifiers provided corroboration. |
| **3** | **Institutional / Authority** | `is_institutional == True` OR `authority_score >= 0.8` | Signal from an institutional, official, or primary authority source. |
| **4** | **Direct Documented Evidence** | `primary_evidence == True` OR `document_hash != None` | Direct documented evidence (PDF, scan, transcript hash) is attached. |

## Deterministic Priorities

The classifier follows a strict top-down priority. The highest matching level is assigned:

1. **Level 4 (Direct Evidence)**
2. **Level 3 (Institutional Authority)**
3. **Level 2 (Multi-Source)**
4. **Level 1 (Single-Source)**
5. **Level 0 (Unverified)**

## Source Signal Definitions

*   `source_hash`: Canonical source identifier (provided by hashing layer).
*   `source_id`: Fallback unique source identifier.
*   `is_institutional`: Boolean flag for official/institutional sources.
*   `authority_score`: Normalized score [0-1] for source reliability.
*   `primary_evidence`: Boolean flag for direct, first-party documented evidence.
*   `document_hash`: Unique cryptographic hash of a primary source document.

No probabilistic inference, interpretative AI judgment, or heuristic optimism is permitted in this layer.
