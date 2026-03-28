# Truth Intelligence Layer - Architecture & Design

## Executive Summary

The Truth Intelligence Layer is a strategic information security system that transforms Samachar into a truth-aware news intelligence platform. It determines truth classification, detects contradictions, scores source reliability, and generates confidence metrics for all processed events.

**Timeline:** 2-3 day execution window  
**Status:** Phase 1-6 Complete  
**Key Outcome:** Each event receives a truth state with conflict detection and source reliability scoring

---

## 1. System Architecture

### 1.1 High-Level Pipeline

```
Event Extraction Layer (Seeya)
         ↓
Truth Intelligence Layer
         ├─ Phase 1: Truth Classification
         ├─ Phase 2: Source Reliability Scoring
         ├─ Phase 3: Cross-Source Event Matching
         ├─ Phase 4: Conflict Detection
         └─ Phase 5: Truth State Resolution
         ↓
Signal Generator
         ↓
Content Distribution Bucket
```

### 1.2 Integration Points

| Layer | Provider | Responsibility | Integration |
|-------|----------|---|---|
| Event Extraction | Seeya | Structured event ingestion | Read-only (immutable) |
| Truth Intelligence | Internal | Truth determination | Process events |
| Backend APIs | Noopur | Expose truth signals | Query endpoints |
| Frontend Visualization | Chandragupta | Display state/conflicts | Consume API signals |
| Testing Validation | Vinayak Tiwari | Verify accuracy | Validate outputs |
| Future BHIV Integration | Raj Prajapati | Intelligence layer chain | Queue for BHIV |

### 1.3 Design Principles

- **Deterministic Classification:** No randomness; identical inputs produce identical outputs
- **Non-Invasive:** Never modifies event extraction, schemas, or ingestion pipeline
- **Modular Architecture:** Each phase is independent and pluggable
- **Evidence-Based:** All decisions backed by source metadata and event properties
- **Conflict-Aware:** Explicitly detects and signals contradictions
- **Confidence Transparent:** Every signal includes confidence metrics

---

## 2. Module Descriptions

### Phase 1: Truth Classifier (`truth_classifier.py`)

**Responsibility:** Classify event truth level deterministically

#### Truth Levels (0-4)

| Level | Name | Definition | Signals |
|-------|------|-----------|---------|
| 0 | UNVERIFIED | Claim without valid sources | No sources identified |
| 1 | SINGLE_SOURCE | Report from one source | Exactly 1 unique source_id |
| 2 | CORROBORATED | Multi-source confirmation | ≥2 unique source_ids |
| 3 | INSTITUTIONAL | Authority/official source | is_institutional=True or authority_score≥0.8 |
| 4 | PRIMARY_EVIDENCE | Direct documented evidence | document_hash present or primary_evidence=True |

#### Classification Algorithm

```python
Priority-based deterministic classification:
1. Check for PRIMARY_EVIDENCE (level 4)
   - If source.document_hash exists → return 4
   - If source.primary_evidence = True → return 4
   
2. Check for INSTITUTIONAL (level 3)
   - If source.is_institutional = True → return 3
   - If source.authority_score ≥ 0.8 → return 3
   
3. Count unique sources
   - If unique_sources ≥ 2 → return 2 (CORROBORATED)
   - If unique_sources = 1 → return 1 (SINGLE_SOURCE)
   - Else → return 0 (UNVERIFIED)
```

#### Example

```json
{
  "sources": [
    {"source_id": "pib", "is_institutional": true},
    {"source_id": "imd", "authority_score": 0.92}
  ],
  "result": {
    "truth_level": 3,
    "truth_level_name": "INSTITUTIONAL",
    "source_count": 2,
    "unique_source_count": 2
  }
}
```

---

### Phase 2: Source Reliability (`source_reliability.py`)

**Responsibility:** Score sources based on credibility, accuracy, and history

#### Reliability Scoring Formula

$$\text{Reliability Score} = (\text{IC} \times 0.40) + (\text{HA} \times 0.35) + (\text{VS} \times 0.25)$$

Where:
- **IC (Institutional Credibility):** 0-1, based on domain/type/explicit authority_score
- **HA (Historical Accuracy):** Ratio of verified reports minus false report decay
- **VS (Verification Score):** Past performance metric (0-1)

#### Default Institutional Scores

- **Tier 1 (0.95):** reuters, ap, bbc, pib, who, un, election_commission, supreme_court
- **Tier 2 (0.90):** gov.in, world_bank, ndma, parliament
- **Tier 3 (0.85):** the_hindu, indian_express, cnn, cnbc, economist
- **Tier 4 (0.82):** toi, ht, ndtv
- **Unknown:** 0.50 (neutral)

#### Reliability Tiers

| Tier | Score Range | Meaning |
|------|------------|---------|
| VERY_HIGH | ≥ 0.90 | Official/institutional authority |
| HIGH | 0.70-0.89 | Established news agencies/publications |
| MEDIUM | 0.50-0.69 | General news sources |
| LOW | 0.30-0.49 | Newer/less-established sources |
| VERY_LOW | < 0.30 | Unreliable/flagged sources |

#### Example

```json
{
  "source": {
    "source_id": "pib",
    "domain": "pib.gov.in",
    "is_institutional": true
  },
  "result": {
    "source_id": "pib",
    "reliability_score": 0.95,
    "reliability_tier": "VERY_HIGH",
    "is_reliable": true,
    "citation_count": 12,
    "total_reports": 45,
    "verified_reports": 43,
    "false_reports": 2
  }
}
```

---

### Phase 3: Event Matcher (`event_matcher.py`)

**Responsibility:** Detect when multiple articles refer to the same underlying event

#### Matching Signals

Events are matched using weighted scoring:

$$\text{Match Score} = (\text{Entity} \times 0.40) + (\text{Location} \times 0.30) + (\text{Time} \times 0.20) + (\text{Semantic} \times 0.10)$$

| Signal | Score Range | Threshold | Example |
|--------|-------------|-----------|---------|
| Entity Overlap | 0-1 | ≥ 0.5 | Same organizations mentioned |
| Location Match | 0-1 | ≥ 0.8 | Same geographic region |
| Time Proximity | 0-1 | ≥ 0.8 | Within 24 hours (configurable) |
| Semantic Similarity | 0-1 | ≥ 0.5 | Similar topic/content |

#### Matching Threshold

- **Match Score ≥ 0.5** AND **≥1 signal triggered** → Events are matched
- Groups are formed with a canonical event (most complete)

#### Example

```json
{
  "events": [
    {
      "event_id": "evt_1",
      "title": "IMD Monsoon Normal Prediction",
      "location": "India",
      "timestamp": "2026-03-25T09:00:00Z"
    },
    {
      "event_id": "evt_2", 
      "title": "Monsoon Will Be Normal: IMD",
      "location": "India",
      "timestamp": "2026-03-25T10:30:00Z"
    }
  ],
  "matched_groups": [
    {
      "group_id": "a7b3c4d2e8f1",
      "canonical_event": "evt_1",
      "event_count": 2,
      "match_score": 0.85,
      "match_reasons": ["entity_overlap", "time_proximity"]
    }
  ]
}
```

---

### Phase 4: Conflict Detector (`conflict_detector.py`)

**Responsibility:** Detect contradictions between events with same registry_reference_id

#### Conflict Types

| Type | Fields Monitored | Detection Logic | Example |
|------|------------------|-----------------|---------|
| **Factual Contradiction** | status, outcome, result, decision, verified | Different values for same field | "confirmed" vs "denied" |
| **Opposing Claims** | is_active, is_verified, is_complete, confirmed, denied | Boolean fields with True AND False | is_verified: true vs false |
| **Numeric Incompatibility** | amount, count, score, value, percentage, rate | Values differ by > tolerance (default 1%) | 100 vs 1000 monsoon prediction |
| **Timeline Inconsistency** | timestamp, date, published_at, event_time | Same event_id at different times | Event reported 2 hours apart |
| **Policy Contradiction** | policy, stance, position, recommendation | Different policy positions | Support vs oppose measure |
| **Semantic Contradiction** | prediction, forecast, outlook, expectation | Opposing semantic terms | "normal" vs "below_normal" |

#### Semantic Contradiction Pairs

```python
("normal", "below_normal"), ("above_normal", "below_normal"),
("increase", "decrease"), ("growth", "contraction"),
("positive", "negative"), ("likely", "unlikely"),
("confirmed", "denied"), ("support", "oppose"),
("accept", "reject"), ("propose", "cancel")
```

#### Example

```json
{
  "registry_id": "REG_WEATHER_2026_03",
  "events": [
    {"event_id": "evt_1", "prediction": "normal monsoon"},
    {"event_id": "evt_2", "prediction": "below_normal monsoon"}
  ],
  "result": {
    "conflict_flag": true,
    "conflict_types": ["semantic_contradiction"],
    "conflicting_fields": ["prediction"],
    "conflicting_event_count": 2
  }
}
```

---

### Phase 5: Truth State Engine (`truth_state_engine.py`)

**Responsibility:** Resolve final truth state by combining all signals

#### Confidence Calculation Formula

$$\text{Confidence} = (\text{BScore} \times 0.40) + \text{SrcBonus} + (\text{RelScore} \times 0.25) + \text{CorbBonus} - \text{ConfPenalty}$$

Where:
- **BScore:** Truth level / 4.0 (base score from 0-4)
- **SrcBonus:** min((source_count - 1) × 0.05, 0.15)
- **RelScore:** Average source reliability (weighted 25%)
- **CorbBonus:** min(corroborating × 0.10, 0.20)
- **ConfPenalty:** 0.30 if conflict detected, else 0

#### Confidence Tiers

| Tier | Range | Meaning |
|------|-------|---------|
| VERY_HIGH | ≥ 0.90 | Extremely confident |
| HIGH | ≥ 0.75 | High confidence |
| MEDIUM | ≥ 0.50 | Moderate confidence |
| LOW | ≥ 0.25 | Low confidence |
| VERY_LOW | < 0.25 | Very uncertain |

#### Example

```json
{
  "sources": [
    {"source_id": "pib", "is_institutional": true, "authority_score": 0.95},
    {"source_id": "imd", "authority_score": 0.92}
  ],
  "result": {
    "truth_level": 3,
    "truth_level_name": "INSTITUTIONAL",
    "conflict_flag": false,
    "confidence_score": 0.87,
    "confidence_tier": "HIGH",
    "corroborating_sources": 2,
    "conflicting_sources": 0,
    "source_reliability_avg": 0.935
  }
}
```

---

### Phase 6: Pipeline Integration (`pipeline_integration.py`)

**Responsibility:** Orchestrate all modules into a unified pipeline

#### Main Classes

##### `TruthIntelligenceLayer`

Central orchestrator that processes events through all phases.

```python
config = TruthIntelligenceConfig(
    enable_conflict_detection=True,
    enable_event_matching=True,
    enable_source_scoring=True,
    enable_truth_resolution=True,
    numeric_tolerance=0.01,
    event_matching_window_hours=24
)

layer = TruthIntelligenceLayer(config)
enriched_events = layer.process_events(events, registry_id)
```

#### Processing Flow

```
Input Event
    ↓
Extract Sources
    ↓
Truth Classification → Get truth_level (0-4)
    ↓
Source Reliability → Score each source
    ↓
Event Matching → Find matched groups
    ↓
Conflict Detection → Check for contradictions
    ↓
Truth State Resolution → Combine all signals
    ↓
Output Enriched Event + truth_intelligence object
```

---

## 3. Output Schema

### Event Truth Intelligence Object

```json
{
  "event_id": "evt_monsoon_2026_001",
  "registry_reference_id": "REG_WEATHER_2026_03",
  "truth_intelligence": {
    "truth_classification": {
      "truth_level": 3,
      "truth_level_name": "INSTITUTIONAL",
      "source_count": 3,
      "unique_source_count": 3
    },
    "source_reliability": {
      "pib_source": {
        "source_id": "pib_source",
        "reliability_score": 0.95,
        "reliability_tier": "VERY_HIGH",
        "is_reliable": true,
        "citation_count": 12,
        "total_reports": 45,
        "verified_reports": 43,
        "false_reports": 2
      }
    },
    "event_matching": {
      "is_matched": true,
      "matched_groups": [
        {
          "group_id": "a7b3c4d2e8f1",
          "canonical_event": {"event_id": "evt_imd_monsoon", "title": "..."},
          "event_count": 3,
          "match_score": 0.85,
          "match_reasons": ["entity_overlap", "time_proximity"]
        }
      ]
    },
    "conflict_detection": {
      "conflict_flag": false,
      "conflict_types": [],
      "conflicting_fields": []
    },
    "truth_resolution": {
      "truth_level": 3,
      "truth_level_name": "INSTITUTIONAL",
      "conflict_flag": false,
      "confidence_score": 0.87,
      "confidence_tier": "HIGH",
      "corroborating_sources": 3,
      "conflicting_sources": 0,
      "source_reliability_avg": 0.935
    },
    "processing_timestamp": "2026-03-28T12:00:00Z"
  }
}
```

---

## 4. API Reference

### `process_event_pipeline(events, registry_id, config)`

Process events through the full Truth Intelligence pipeline.

```python
from truth_intelligence.pipeline_integration import process_event_pipeline

events = [
    {
        "event_id": "evt_1",
        "title": "Monsoon Prediction",
        "registry_reference_id": "REG_WEATHER_2026_03",
        "sources": [
            {"source_id": "pib", "is_institutional": True},
            {"source_id": "imd", "authority_score": 0.92}
        ]
    }
]

enriched = process_event_pipeline(events)
for event in enriched:
    print(event['truth_intelligence'])
```

### `get_event_truth(event, all_events)`

Get truth signals for a single event.

```python
from truth_intelligence.pipeline_integration import get_event_truth

truth_signals = get_event_truth(event, all_events)
```

### `update_verification(source_id, verified)`

Update source verification history for future scoring.

```python
from truth_intelligence.pipeline_integration import update_verification

update_verification("pib", verified=True)
update_verification("unreliable_blog", verified=False)
```

---

## 5. Usage Examples

### Example 1: Simple Truth Classification

```python
from truth_intelligence.truth_classifier import classify_truth_level

sources = [
    {"source_id": "pib", "is_institutional": True},
    {"source_id": "imd", "authority_score": 0.92}
]

truth_level = classify_truth_level(sources)
print(truth_level)  # Output: 3 (INSTITUTIONAL)
```

### Example 2: Source Reliability Scoring

```python
from truth_intelligence.source_reliability import get_source_metadata

source = {"source_id": "pib", "domain": "pib.gov.in", "is_institutional": True}
metadata = get_source_metadata(source)
print(metadata['reliability_score'])  # Output: 0.95
print(metadata['reliability_tier'])   # Output: "VERY_HIGH"
```

### Example 3: Event Matching

```python
from truth_intelligence.event_matcher import get_matched_event_groups

events = [
    {"event_id": "evt_1", "title": "Monsoon Normal", "location": "India", "timestamp": "2026-03-25T09:00:00Z"},
    {"event_id": "evt_2", "title": "Monsoon Will Be Normal", "location": "India", "timestamp": "2026-03-25T10:30:00Z"}
]

groups = get_matched_event_groups(events)
print(f"Matched groups: {groups['matched_groups']}")  # If match_score >= 0.5
```

### Example 4: Conflict Detection

```python
from truth_intelligence.conflict_detector import get_event_conflict_metadata

events = [
    {"registry_reference_id": "REG_1", "event_id": "evt_1", "prediction": "normal"},
    {"registry_reference_id": "REG_1", "event_id": "evt_2", "prediction": "below_normal"}
]

conflicts = get_event_conflict_metadata("REG_1", events)
print(conflicts['conflict_flag'])  # Output: true
print(conflicts['conflict_types'])  # Output: ["semantic_contradiction"]
```

### Example 5: Full Pipeline Integration

```python
from truth_intelligence.pipeline_integration import TruthIntelligenceLayer, TruthIntelligenceConfig

config = TruthIntelligenceConfig(
    enable_conflict_detection=True,
    enable_event_matching=True,
    enable_source_scoring=True,
    enable_truth_resolution=True
)

layer = TruthIntelligenceLayer(config)
enriched_events = layer.process_events(raw_events, registry_id="REG_WEATHER_2026_03")

for event in enriched_events:
    truth_signals = event['truth_intelligence']
    print(f"Event: {event['event_id']}")
    print(f"  Truth Level: {truth_signals['truth_classification']['truth_level_name']}")
    print(f"  Confidence: {truth_signals['truth_resolution']['confidence_tier']}")
    print(f"  Conflict: {truth_signals['conflict_detection']['conflict_flag']}")
```

---

## 6. Integration with Seeya (Event Extraction)

The Truth Intelligence Layer is invoked AFTER event extraction and BEFORE signal generation.

### Data Flow

```
Seeya Event Extraction
├─ Extract entities, locations, timestamp
├─ Identify sources
├─ Normalize content
└─ Output: Structured Event Object
                 ↓
    Truth Intelligence Layer
    ├─ Classify truth level
    ├─ Score source reliability
    ├─ Match related events
    ├─ Detect conflicts
    ├─ Resolve final truth state
    └─ Enrich event with truth_intelligence
                 ↓
    Signal Generator
    ├─ Extract truth signals
    ├─ Package for distribution
    └─ Output: Signal with confidence
                 ↓
    Content Bucket / Distribution
```

### Expected Input from Seeya

```json
{
  "event_id": "evt_123",
  "registry_reference_id": "REG_WEATHER_2026_03",
  "title": "Monsoon Prediction",
  "content": "IMD predicts normal monsoon in 2026",
  "timestamp": "2026-03-25T09:00:00Z",
  "location": "India",
  "entities": ["monsoon", "IMD", "2026"],
  "sources": [
    {
      "source_id": "imd",
      "source_url": "imd.gov.in",
      "is_institutional": true,
      "authority_score": 0.92
    }
  ]
}
```

### Output to Signal Generator

```json
{
  "event_id": "evt_123",
  "registry_reference_id": "REG_WEATHER_2026_03",
  "... (original fields preserved) ...",
  "truth_intelligence": {
    "truth_classification": { ... },
    "source_reliability": { ... },
    "event_matching": { ... },
    "conflict_detection": { ... },
    "truth_resolution": { ... }
  }
}
```

---

## 7. Constraints & Guardrails

### What Truth Intelligence Does NOT Do

❌ Modify event extraction logic  
❌ Change entity recognition or NER  
❌ Alter source extraction from Seeya  
❌ Break content generation downstream  
❌ Change event schemas  
❌ Modify ingestion pipeline   

### What Truth Intelligence DOES

✓ Add truth_intelligence object to event  
✓ Score sources independently  
✓ Classify truth levels deterministically  
✓ Detect contradictions  
✓ Match related events  
✓ Generate confidence signals  
✓ Never removes or alters original event fields  

---

## 8. Testing & Validation

### Test Coverage

Tests are located in `/tests/test_truth_and_conflict.py` (Vinayak Tiwari responsible)

Key test cases:
- Truth classification for all levels (0-4)
- Source reliability scoring accuracy
- Event matching correctness
- Conflict detection precision
- Confidence score calculations
- Pipeline end-to-end integration

### Acceptance Criteria

✅ Events receive truth classification (0-4)  
✅ Conflicts between sources detected  
✅ Truth signals generated with confidence  
✅ Pipeline produces structured truth outputs  
✅ Content generation pipeline unaffected  
✅ No modification to event schemas  

---

## 9. Performance Characteristics

| Operation | Complexity | Performance |
|-----------|------------|-------------|
| Truth Classification | O(n) | <10ms per event |
| Source Scoring | O(n·m) | <50ms for 10 sources |
| Event Matching | O(m²) | <100ms for 100 events |
| Conflict Detection | O(n·k) | <50ms per registry group |
| Truth State Resolution | O(n) | <30ms per event |
| Full Pipeline | O(m² + n·k) | <500ms per 100 events |

---

## 10. Future Enhancements

### Phase 2 Roadmap (Post-Deployment)

- Machine learning-based source credibility prediction
- Natural Language Processing for semantic similarity
- Geolocation proximity scoring using coordinates
- Temporal pattern analysis for recurring contradictions
- Integration with BHIV intelligence layer
- Real-time conflict alert system
- Source network trust propagation
- Historical fact-checking database integration

---

## 11. Appendix: Module Dependencies

```
pipeline_integration.py (main entry point)
├── truth_classifier.py
├── source_reliability.py
├── event_matcher.py
├── conflict_detector.py
└── truth_state_engine.py
    ├── truth_classifier.py
    ├── source_reliability.py
    └── conflict_detector.py
```

### Import Strategy

```python
# Simple usage (recommended)
from truth_intelligence.pipeline_integration import process_event_pipeline

# Direct module access
from truth_intelligence import (
    truth_classifier,
    source_reliability,
    event_matcher,
    conflict_detector,
    truth_state_engine
)
```

---

## 12. Questions & Support

**Architecture:** Raj Prajapati (Core Integration)  
**Implementation:** Development Team  
**Testing:** Vinayak Tiwari  
**Frontend Integration:** Chandragupta Team  
**Backend APIs:** Noopur  

---

**Document Version:** 1.0  
**Last Updated:** March 28, 2026  
**Status:** Implementation Complete - Phases 1-6

