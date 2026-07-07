# News-AI (Samachar) + Intake Intelligence Engine Integration

## Overview

This review packet contains the intentionally modified files required to integrate the Intake Intelligence Engine into the News-AI backend.

The integration enriches the existing news analysis pipeline by adding an explainable intelligence layer without affecting the existing News-AI functionality.

---

## Integrated Features

- Entity Extraction
- Entity Validation
- News Classification
- Evidence Generation
- Confidence Scoring
- Processing Trace

---

## Design Goals

- Preserve the existing News-AI architecture.
- Keep the integration modular.
- Avoid breaking existing API contracts.
- Produce explainable intelligence instead of black-box predictions.

---

## Review Order

Please review the files in the following order:

1. `news_intelligence_service.py`
2. `entity_extractor.py`
3. `entity_validator.py`
4. `classification_engine.py`
5. `evidence_engine.py`
6. `confidence_engine.py`

---

## Expected API Output

The integration adds an `intelligence` object to the response containing:

- validated_entities
- classification
- evidence
- confidence
- processing_trace
- rejected_entities

No existing News-AI response fields were removed or modified.