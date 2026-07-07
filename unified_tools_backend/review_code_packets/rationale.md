# Design Rationale

## Why an Adapter Layer?

Instead of modifying the existing News-AI services, a dedicated `NewsIntelligenceService` was introduced.

Benefits:

- Low coupling
- Easier maintenance
- Preserves existing pipeline
- Modular integration

---

## Why News-Specific Classification?

The original Intake Intelligence Engine was designed for multiple document types.

For News-AI (Samachar), the classifier was adapted with news-oriented domains such as:

- Politics
- Business
- Sports
- Technology
- Health
- Environment
- Entertainment
- Crime
- World
- Education

This significantly improves classification accuracy for news articles.

---

## Why Explainable Intelligence?

Every classification now includes:

- supporting entities
- matched keywords
- evidence
- confidence
- processing trace

This improves transparency and simplifies debugging.