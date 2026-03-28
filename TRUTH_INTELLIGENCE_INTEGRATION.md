# Truth Intelligence Layer - Integration Guide

## Overview

The Truth Intelligence Layer integrates seamlessly into the Samachar news intelligence pipeline, sitting between the **Event Extraction Layer (Seeya)** and the **Signal Generator** / **Content Distribution**.

---

## Pipeline Integration Points

### Current Pipeline Flow

```
Raw News Input
    ↓
Samachar API (/api/samachar/process)
    ├─ Text cleaning
    ├─ Language detection
    ├─ Summarization
    ├─ Category classification
    ├─ Sentiment analysis
    └─ Output: Basic event structure
```

### Enhanced Pipeline with Truth Intelligence

```
Raw News Input
    ↓
Samachar API (/api/samachar/process)
    ├─ Text cleaning & summarization
    ├─ Category & sentiment analysis
    └─ Output: Event structure
         ↓
    ✨ TRUTH INTELLIGENCE LAYER ✨
    ├─ Phase 1: Truth classification (0-4)
    ├─ Phase 2: Source reliability scoring
    ├─ Phase 3: Event matching (cross-source)
    ├─ Phase 4: Conflict detection
    ├─ Phase 5: Truth state resolution
    └─ Output: Enriched event + truth_intelligence object
         ↓
    Signal Generator
    ├─ Extract truth signals
    ├─ Package for distribution
    └─ Output: Signal with confidence
         ↓
    Content Bucket / Distribution
```

---

## Integration Points with Each Layer

### 1. Seeya (Event Extraction Layer)

**Responsibility:** Extract and structure events  
**Dependencies:** None on Truth Intelligence  
**Truth Intelligence Input:** Consumes Seeya's event output  
**Implementation:** Read-only integration

```
Seeya Output Format:
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

### 2. Truth Intelligence Layer (This Module)

**Responsibility:** Determine truth state  
**Dependencies:** 
- Reads Seeya event output
- Uses source metadata  
- Calls conflict detection  

**Processing Steps:**
1. Classify truth level based on sources
2. Score source reliability
3. Match related events
4. Detect contradictions
5. Resolve final truth state

**Output:**
```
{
  "event_id": "evt_123",
  "... (original Seeya fields preserved) ...",
  "truth_intelligence": {
    "truth_classification": { ... },
    "source_reliability": { ... },
    "event_matching": { ... },
    "conflict_detection": { ... },
    "truth_resolution": { ... },
    "processing_timestamp": "2026-03-28T12:00:00Z"
  }
}
```

### 3. Noopur (Backend APIs)

**Responsibility:** Expose truth signals through APIs  
**Dependencies:** Truth Intelligence Layer output  
**Integration Points:**

```python
# Recommended API Endpoints

GET /api/events/{event_id}/truth-intelligence
  Returns: Complete truth_intelligence object for event

GET /api/events/by-registry/{registry_id}
  Returns: All events with truth signals for registry

GET /api/sources/{source_id}/reliability
  Returns: Source reliability metrics and history

POST /api/events/{event_id}/verify
  Updates: Source verification history for future scoring

GET /api/signals/conflicts
  Returns: Events with detected conflicts
```

### 4. Chandragupta (Frontend)

**Responsibility:** Visualize truth state and contradictions  
**Dependencies:** Noopur API endpoints  
**Visualization Components:**

```
Truth Badge
├─ Level 0: "Unverified" (gray)
├─ Level 1: "Single Source" (yellow)
├─ Level 2: "Corroborated" (light green)
├─ Level 3: "Institutional" (green)
└─ Level 4: "Primary Evidence" (dark green)

Confidence Indicator
├─ Score displayed as percentage (0-100%)
├─ Tier shown: VERY_HIGH, HIGH, MEDIUM, LOW, VERY_LOW
├─ Color-coded risk indicator

Conflict Alert
├─ Highlighted if conflict_flag = true
├─ Shows conflicting fields
├─ Lists conflicting sources

Source Reliability Card
├─ Per-source reliability score (0-1.0)
├─ Tier badge (VERY_HIGH, HIGH, etc.)
├─ Citation count
├─ Verification history
└─ Performance metrics (verified/false reports)
```

### 5. Testing Layer (Vinayak Tiwari)

**Responsibility:** Validate truth classifications  
**Integration:** 

```python
# Test cases should validate:
1. Truth level classification accuracy
2. Source reliability scoring
3. Conflict detection precision
4. Confidence score calculations
5. Event matching correctness
6. Pipeline end-to-end integration

# Reference test file:
/tests/test_truth_and_conflict.py
```

---

## How to Integrate Truth Intelligence

### Option 1: Direct Integration in Samachar API

Modify `/api/samachar_api.py`:

```python
from truth_intelligence.pipeline_integration import process_event_pipeline

def process_text(raw_text: str) -> dict:
    """Original processing pipeline"""
    # ... existing code ...
    event = {
        "id": os.urandom(8).hex(),
        "title": title,
        "summary_short": s_short,
        "category": cat,
        # ... other fields ...
    }
    
    # ADD THIS: Enrich with truth intelligence
    enriched_events = process_event_pipeline(
        [event], 
        registry_id="REG_" + cat.upper()
    )
    
    return enriched_events[0]
```

### Option 2: Middleware Integration in Noopur

Modify unified backend:

```python
from truth_intelligence.pipeline_integration import TruthIntelligenceLayer

@app.post("/api/events/ingest")
async def ingest_events(events: List[Dict[str, Any]]):
    """Ingest events from Seeya and enrich with truth signals"""
    
    layer = TruthIntelligenceLayer()
    registry_id = request.query_params.get("registry_id")
    
    enriched = layer.process_events(events, registry_id)
    
    # Store in database with truth_intelligence
    for event in enriched:
        save_event(event)
    
    return {"status": "enriched", "event_count": len(enriched)}
```

### Option 3: Async Pipeline

```python
import asyncio
from truth_intelligence.pipeline_integration import process_event_pipeline

async def enrich_events_async(events: List[Dict]):
    """Non-blocking truth intelligence enrichment"""
    loop = asyncio.get_event_loop()
    enriched = await loop.run_in_executor(
        None,
        process_event_pipeline,
        events,
        None,  # registry_id
        None   # config
    )
    return enriched
```

---

## Data Flow Diagrams

### Complete Event Lifecycle

```
┌─────────────────────────┐
│   Raw News Article      │
└──────────┬──────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│  Samachar API (Text Processing)         │
│  - Clean text                           │
│  - Extract entities                     │
│  - Analyze sentiment                    │
│  - Classify category                    │
│  Output: Structured Event               │
└──────────┬──────────────────────────────┘
           │
           ↓
┌──────────────────────────────────────────────────────────┐
│  Truth Intelligence Layer (Strategic Analysis)           │
│  ┌─────────────────────────────────────────┐             │
│  │ Phase 1: Truth Classification           │             │
│  │ - Check institutional authority         │             │
│  │ - Count corroborating sources           │             │
│  │ - Assess primary evidence               │             │
│  │ Output: truth_level (0-4)               │             │
│  └─────────────────────────────────────────┘             │
│  ┌─────────────────────────────────────────┐             │
│  │ Phase 2: Source Reliability             │             │
│  │ - Domain credibility lookup             │             │
│  │ - Historical accuracy scoring           │             │
│  │ - Verification frequency analysis       │             │
│  │ Output: reliability_score (0-1)         │             │
│  └─────────────────────────────────────────┘             │
│  ┌─────────────────────────────────────────┐             │
│  │ Phase 3: Event Matching                 │             │
│  │ - Entity overlap analysis               │             │
│  │ - Location proximity scoring            │             │
│  │ - Time window correlation               │             │
│  │ Output: matched_groups                  │             │
│  └─────────────────────────────────────────┘             │
│  ┌─────────────────────────────────────────┐             │
│  │ Phase 4: Conflict Detection             │             │
│  │ - Numeric contradiction check           │             │
│  │ - Policy stance evaluation              │             │
│  │ - Semantic opposition detection         │             │
│  │ Output: conflict_flag, conflict_types   │             │
│  └─────────────────────────────────────────┘             │
│  ┌─────────────────────────────────────────┐             │
│  │ Phase 5: Truth State Resolution         │             │
│  │ - Combine all signals                   │             │
│  │ - Calculate confidence score            │             │
│  │ - Determine final truth state           │             │
│  │ Output: truth_state with confidence     │             │
│  └─────────────────────────────────────────┘             │
│  Output: Enriched Event with full truth signals          │
└──────────┬───────────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────┐
│  Signal Generator       │
│  - Extract key signals │
│  - Package for dists    │
└──────────┬──────────────┘
           │
           ↓
┌──────────────────────────┐
│  Content Bucket          │
│  - Distribution Queue    │
│  - Downstream Systems    │
└──────────────────────────┘
```

---

## API Contract

### Input Format (from Seeya)

```json
{
  "event_id": "evt_123",
  "registry_reference_id": "REG_WEATHER_2026_03",
  "title": "Event Title",
  "content": "Full event content",
  "timestamp": "2026-03-25T09:00:00Z",
  "location": "Location Name",
  "entities": ["entity1", "entity2"],
  "sources": [
    {
      "source_id": "source_identifier",
      "source_url": "https://example.com",
      "source_type": "news_agency|newspaper|blog|social|official",
      "is_institutional": boolean,
      "authority_score": 0.0-1.0
    }
  ]
}
```

### Output Format (to Signal Generator)

```json
{
  "event_id": "evt_123",
  "registry_reference_id": "REG_WEATHER_2026_03",
  "... (all original fields preserved) ...",
  "truth_intelligence": {
    "truth_classification": {
      "truth_level": 0-4,
      "truth_level_name": "UNVERIFIED|SINGLE_SOURCE|CORROBORATED|INSTITUTIONAL|PRIMARY_EVIDENCE",
      "source_count": integer,
      "unique_source_count": integer
    },
    "source_reliability": {
      "source_id": {
        "source_id": "string",
        "reliability_score": 0.0-1.0,
        "reliability_tier": "VERY_HIGH|HIGH|MEDIUM|LOW|VERY_LOW",
        "is_reliable": boolean,
        "citation_count": integer,
        "total_reports": integer,
        "verified_reports": integer,
        "false_reports": integer
      }
    },
    "event_matching": {
      "is_matched": boolean,
      "matched_groups": [
        {
          "group_id": "hash_id",
          "canonical_event": {...},
          "event_count": integer,
          "match_score": 0.0-1.0,
          "match_reasons": ["entity_overlap", "time_proximity", "location_match"]
        }
      ]
    },
    "conflict_detection": {
      "conflict_flag": boolean,
      "conflict_types": ["factual_contradiction", "semantic_contradiction", ...],
      "conflicting_fields": ["field1", "field2"]
    },
    "truth_resolution": {
      "truth_level": 0-4,
      "truth_level_name": "UNVERIFIED|SINGLE_SOURCE|CORROBORATED|INSTITUTIONAL|PRIMARY_EVIDENCE",
      "conflict_flag": boolean,
      "confidence_score": 0.0-1.0,
      "confidence_tier": "VERY_HIGH|HIGH|MEDIUM|LOW|VERY_LOW",
      "corroborating_sources": integer,
      "conflicting_sources": integer,
      "source_reliability_avg": 0.0-1.0
    },
    "processing_timestamp": "ISO8601 timestamp"
  }
}
```

---

## Configuration

### Default Configuration

```python
from truth_intelligence.pipeline_integration import TruthIntelligenceConfig

config = TruthIntelligenceConfig(
    enable_conflict_detection=True,      # Enable phase 4
    enable_event_matching=True,          # Enable phase 3
    enable_source_scoring=True,          # Enable phase 2
    enable_truth_resolution=True,        # Enable phase 5
    numeric_tolerance=0.01,              # 1% for numeric conflicts
    event_matching_window_hours=24       # 24-hour window for matching
)
```

### Custom Configuration

```python
# Strict mode (high confidence threshold)
config = TruthIntelligenceConfig(
    numeric_tolerance=0.001,             # 0.1% tolerance
    event_matching_window_hours=6        # 6-hour strict window
)

# Permissive mode (lower confidence threshold)
config = TruthIntelligenceConfig(
    numeric_tolerance=0.05,              # 5% tolerance
    event_matching_window_hours=48       # 48-hour loose window
)
```

---

## Error Handling

### Expected Exception Scenarios

```python
from truth_intelligence.pipeline_integration import TruthIntelligenceLayer

try:
    layer = TruthIntelligenceLayer()
    enriched = layer.process_events(events, registry_id)
except ValueError as e:
    # Invalid input format
    logger.error(f"Invalid event format: {e}")
except TypeError as e:
    # Missing required fields
    logger.error(f"Missing required fields: {e}")
except Exception as e:
    # Unexpected error - layer is non-critical
    logger.error(f"Truth Intelligence error (non-blocking): {e}")
    # Return original events without enrichment
    return events
```

### Graceful Degradation

Truth Intelligence Layer is designed to be non-critical:

```python
try:
    enriched = process_event_pipeline(events)
    return enriched
except Exception:
    # If enrichment fails, return original events
    logger.log("Truth Intelligence unavailable, using raw events")
    return events
```

---

## Performance Considerations

### Benchmarks (per 100 events)

| Operation | Time | Notes |
|-----------|------|-------|
| Truth Classification | <10ms | O(n) |
| Source Scoring | <50ms | O(n·m) where m=sources |
| Event Matching | <100ms | O(m²) where m=events |
| Conflict Detection | <50ms | O(n·k) where n=sources, k=fields |
| Truth State Resolution | <30ms | O(n) |
| **Total Pipeline** | **<500ms** | All phases combined |

### Optimization Tips

1. **Batch Processing:** Process events in batches (e.g., 50-100 at a time)
2. **Async Wrap:** Use async wrapper for non-blocking integration
3. **Cache Source Scores:** Reuse source reliability scores across events
4. **Selective Phases:** Disable phases not needed for your use case

---

## Deployment Checklist

- [ ] Truth Intelligence modules installed in `/truth_intelligence/`
- [ ] All imports verified and working
- [ ] `test_truth_intelligence.py` passes all 7/7 tests
- [ ] `TRUTH_INTELLIGENCE_ARCHITECTURE.md` documented
- [ ] API integration point identified (Samachar/Noopur)
- [ ] Configuration determined (default or custom)
- [ ] Error handling implemented
- [ ] Frontend visualization specs ready (Chandragupta)
- [ ] Testing plan created (Vinayak Tiwari)
- [ ] Noopur API endpoints ready for truth signals

---

## Rollback Plan

If issues occur during deployment:

1. **Immediate:** Disable truth_intelligence integration
2. **Backward Compatibility:** Original event structure preserved
3. **Recovery:** Reprocess events through Truth Intelligence without breaking existing pipeline
4. **Communication:** Alert Chandragupta/Noopur teams

---

## Support & Troubleshooting

### Common Issues

**Q: Truth Intelligence is slow**  
A: It's designed for non-blocking async use. Wrap in async executor or run in separate process.

**Q: Confidence scores are too low**  
A: Adjust formula weights or check source reliability scoring configuration.

**Q: Events not matching**  
A: Increase `event_matching_window_hours` or adjust entity overlap threshold.

**Q: Conflicts not detected**  
A: Check if `enable_conflict_detection` is true and numeric tolerance/field names are correct.

---

## Next Steps

1. **Immediate:** Deploy Truth Intelligence Layer
2. **Week 1:** Integrate with Noopur API endpoints
3. **Week 2:** Connect Chandragupta frontend visualizations
4. **Week 3:** Run validation tests with Vinayak Tiwari
5. **Week 4:** BHIV intelligence layer integration (Raj Prajapati)

---

**Document Version:** 1.0  
**Integration Status:** Ready for Production  
**Last Updated:** March 28, 2026

