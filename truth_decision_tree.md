# Truth Classification Decision Tree

Deterministic rule-based classification system for truth signals.

## Levels Overview

| Level | Description | Rule |
| :--- | :--- | :--- |
| **0** | **Unverified Claim** | No sources provided or source identifiers are missing. |
| **1** | **Single-Source Report** | Only one unique source identifier found. |
| **2** | **Multi-Source Corroboration** | Two or more unique source identifiers provided. |
| **3** | **Institutional / Authority** | At least one source has `authority_level` >= 3. |
| **4** | **Primary Evidence** | At least one source has `primary_evidence` = True. |

## Classification Logic (Order of Operations)

The classifier follows a strict top-down check:

1. **Check for Level 4**: If any source is flagged as `primary_evidence`, classification is Level 4.
2. **Check for Level 3**: If any source has `authority_level` >= 3, classification is Level 3.
3. **Check for Level 2**: Count unique `source_id`. If count >= 2, classification is Level 2.
4. **Check for Level 1**: If count == 1, classification is Level 1.
5. **Default**: If no sources or missing metadata, classification is Level 0.

## Source Metadata Contract

Each source object should contain:
- `source_id`: (Required for level 1 & 2) A unique identifier for the source (e.g., URL, publisher ID).
- `authority_level`: (Optional) Integer indicating institutional authority.
- `primary_evidence`: (Optional) Boolean flag for direct documented evidence.
