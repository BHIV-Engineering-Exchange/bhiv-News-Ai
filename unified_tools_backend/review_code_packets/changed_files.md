# Intentionally Modified Files

The following files were intentionally modified as part of the integration.

## New Files

analysis/news_intelligence_service.py

analysis/entity_extractor.py

analysis/classification_engine.py

analysis/evidence_engine.py

analysis/confidence_engine.py

validation/entity_validator.py

---

## Existing Files Updated

main.py

---

## Purpose of Changes

| File | Purpose |
|------|---------|
| news_intelligence_service.py | Integrates the Intelligence Engine with News-AI |
| entity_extractor.py | Extracts news entities |
| entity_validator.py | Removes noisy entities and validates results |
| classification_engine.py | Classifies news into domain categories |
| evidence_engine.py | Generates explainable evidence |
| confidence_engine.py | Produces confidence score |
| main.py | Connects News-AI (Samachar) pipeline with Intelligence Engine |