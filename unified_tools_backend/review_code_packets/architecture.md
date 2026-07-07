# Integration Architecture

```
News-AI (Samachar)

↓

Scraping

↓

NewsIntelligenceService

├── Entity Extraction

├── Entity Validation

├── Classification

├── Evidence

├── Confidence

└── Processing Trace

↓

Existing News-AI Pipeline

↓

API Response
```

The integration follows an adapter-based approach, ensuring that the existing News-AI architecture remains unchanged while adding an explainable intelligence layer.