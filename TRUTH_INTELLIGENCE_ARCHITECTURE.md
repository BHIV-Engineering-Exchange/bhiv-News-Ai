# Truth Intelligence Layer Architecture

## Overview

The Truth Intelligence Layer (TIL) is a deterministic system for classifying truth signals, detecting conflicts, and scoring source reliability in the Samachar news intelligence pipeline.

## System Position

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SAMACHAR PIPELINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────────────┐     ┌──────────────┐ │
│  │    Seeya     │────▶│ Truth Intelligence   │────▶│   Chandragupta│ │
│  │  Event       │     │       Layer           │     │   Signal     │ │
│  │  Extraction  │     │                      │     │   Generator  │ │
│  └──────────────┘     └──────────────────────┘     └──────────────┘ │
│                              │                                        │
│                              │                                        │
│                              ▼                                        │
│                       ┌──────────────┐                                │
│                       │   Bucket     │                                │
│                       │  Orchestrator│                                │
│                       └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Truth Classifier (`truth_classifier.py`)

Deterministic classification of truth signals into levels 0-4.

| Level | Name | Signal |
|-------|------|--------|
| 0 | UNVERIFIED | No valid sources |
| 1 | SINGLE_SOURCE | Exactly 1 unique source |
| 2 | CORROBORATED | >=2 unique sources |
| 3 | INSTITUTIONAL | is_institutional=True or authority_score>=0.8 |
| 4 | PRIMARY_EVIDENCE | primary_evidence=True or document_hash |

**Classification Priority:** 4 → 3 → 2 → 1 → 0 (highest wins)

### 2. Source Reliability System (`source_reliability.py`)

Scores sources based on:
- **Institutional credibility** (40%): Domain-based scoring for known institutions
- **Historical accuracy** (35%): Track verified vs false reports
- **Verification reputation** (25%): Past performance scoring

**Reliability Tiers:**
- VERY_HIGH: >= 0.90
- HIGH: >= 0.80
- MEDIUM: >= 0.70
- LOW: >= 0.50
- VERY_LOW: < 0.50

### 3. Event Matcher (`event_matcher.py`)

Detects when multiple articles refer to the same event.

**Matching Signals:**
- Entity overlap (40% weight)
- Location proximity (30% weight)
- Time proximity (20% weight)
- Semantic similarity (10% weight)

### 4. Conflict Detector (`conflict_detector.py`)

Detects structural contradictions between events sharing the same `registry_reference_id`.

**Conflict Types:**
- Factual Contradiction: Different status/outcome values
- Opposing Claim: Conflicting boolean values
- Numeric Incompatibility: Different numeric values
- Timeline Inconsistency: Same event at different times
- Policy Contradiction: Different policy positions
- Semantic Contradiction: Opposing predictions/forecasts

### 5. Truth State Engine (`truth_state_engine.py`)

Combines all signals to produce final truth state.

**Output:**
- `truth_level`: 0-4 classification
- `conflict_flag`: Boolean
- `confidence_score`: 0.0-1.0
- `confidence_tier`: VERY_HIGH/HIGH/MEDIUM/LOW/VERY_LOW
- `corroborating_sources`: Count
- `conflicting_sources`: Count
- `source_reliability_avg`: Average reliability

## Integration

### Pipeline Flow

```
Event Extraction (Seeya)
         │
         ▼
┌─────────────────────────────┐
│   Truth Intelligence Layer  │
│                             │
│  1. Truth Classification    │
│  2. Source Reliability      │
│  3. Event Matching          │
│  4. Conflict Detection      │
│  5. Truth State Resolution  │
└─────────────────────────────┘
         │
         ▼
  Signal Generator (Noopur)
         │
         ▼
       Bucket
```

### Usage

```python
from truth_intelligence import process_event_pipeline, TruthIntelligenceLayer

# Process events through full pipeline
enriched_events = process_event_pipeline(events, registry_id="REG_001")

# Or use the layer directly
layer = TruthIntelligenceLayer()
enriched_event = layer.process_single_event(event, all_events, registry_id)
```

## Key Design Decisions

1. **Deterministic Classification**: No probabilistic inference. All truth signals are based on rule-based signals.

2. **Conflict Flagging Only**: Conflicts are flagged but not resolved. Ambiguity is preserved for downstream systems.

3. **Registry-Based Correlation**: Conflict detection operates only on events sharing the same `registry_reference_id`.

4. **Source Tracking**: Source reliability is tracked globally for consistent scoring across the pipeline.

5. **Modular Design**: Each component can be used independently or as part of the integrated pipeline.

## Constraints

- Does NOT modify ingestion pipeline
- Does NOT change event extraction logic
- Does NOT alter Seeya schemas
- Does NOT affect content generation pipeline
- Plugs into Event Intelligence Layer after Seeya

## Interfaces

### Input (from Seeya)
```json
{
  "event_id": "...",
  "registry_reference_id": "...",
  "sources": [
    {
      "source_id": "...",
      "source_hash": "...",
      "is_institutional": true,
      "authority_score": 0.92,
      "primary_evidence": false,
      "url": "https://pib.gov.in/..."
    }
  ],
  "status": "confirmed",
  "timestamp": "2026-03-25T10:00:00Z"
}
```

### Output (to Chandragupta)
```json
{
  "truth_intelligence": {
    "truth_classification": {
      "truth_level": 3,
      "truth_level_name": "INSTITUTIONAL",
      "source_count": 2,
      "unique_source_count": 2
    },
    "source_reliability": {...},
    "event_matching": {...},
    "conflict_detection": {
      "conflict_flag": false,
      "conflict_types": []
    },
    "truth_resolution": {
      "truth_level": 3,
      "conflict_flag": false,
      "confidence_score": 0.85,
      "confidence_tier": "HIGH",
      "corroborating_sources": 2,
      "conflicting_sources": 0,
      "source_reliability_avg": 0.88
    }
  }
}
```

## Extension Points

1. **Custom Source Scoring**: Override `SourceReliabilityScorer` for domain-specific scoring
2. **Additional Conflict Types**: Extend `ConflictDetector` with domain-specific checks
3. **Semantic Matching**: Integrate NLP models for entity extraction in `EventMatcher`
4. **Verification Feedback**: Use `update_source_verification()` to incorporate human feedback
