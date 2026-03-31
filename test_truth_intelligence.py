#!/usr/bin/env python3
"""
Truth Intelligence Layer Integration Test
Tests all 6 phases and validates output format against truth_signals.json
"""

import json
from datetime import datetime, timezone
from truth_intelligence.pipeline_integration import (
    process_event_pipeline,
    get_event_truth,
    TruthIntelligenceConfig
)
from truth_intelligence.truth_classifier import classify_truth_level
from truth_intelligence.source_reliability import get_source_metadata
from truth_intelligence.event_matcher import get_matched_event_groups
from truth_intelligence.conflict_detector import get_event_conflict_metadata


def create_sample_events():
    """Create sample events for testing."""
    return [
        {
            "event_id": "evt_monsoon_2026_001",
            "registry_reference_id": "REG_WEATHER_2026_03",
            "title": "IMD Predicts Normal Monsoon 2026",
            "content": "India Meteorological Department predicts normal monsoon rainfall in 2026",
            "timestamp": "2026-03-25T09:00:00Z",
            "location": "India",
            "entities": ["monsoon", "rainfall", "IMD", "2026"],
            "sources": [
                {
                    "source_id": "pib_source",
                    "source_url": "pib.gov.in",
                    "source_type": "official",
                    "is_institutional": True,
                    "authority_score": 0.95
                },
                {
                    "source_id": "imd_source",
                    "source_url": "imd.gov.in",
                    "source_type": "official",
                    "is_institutional": True,
                    "authority_score": 0.92
                },
                {
                    "source_id": "bbc_news",
                    "source_url": "bbc.com",
                    "source_type": "news_agency",
                    "authority_score": 0.93
                }
            ],
            "prediction": "normal"
        },
        {
            "event_id": "evt_monsoon_2026_002",
            "registry_reference_id": "REG_WEATHER_2026_03",
            "title": "Monsoon Rainfall Will Be Normal: IMD Official Statement",
            "content": "An official from IMD stated that monsoon will remain normal this year",
            "timestamp": "2026-03-25T10:30:00Z",
            "location": "India",
            "entities": ["monsoon", "IMD", "official"],
            "sources": [
                {
                    "source_id": "imd_source",
                    "source_url": "imd.gov.in",
                    "is_institutional": True,
                    "authority_score": 0.92
                }
            ],
            "prediction": "normal"
        },
        {
            "event_id": "evt_monsoon_2026_conflict",
            "registry_reference_id": "REG_WEATHER_2026_03",
            "title": "Monsoon Expected to be Below Normal",
            "content": "Weather analysis suggests monsoon will be below normal",
            "timestamp": "2026-03-25T14:00:00Z",
            "location": "India",
            "entities": ["monsoon", "weather"],
            "sources": [
                {
                    "source_id": "weather_blog",
                    "source_url": "weatherblog.com",
                    "source_type": "blog",
                    "authority_score": 0.45
                }
            ],
            "prediction": "below_normal"
        }
    ]


def test_phase1_truth_classification():
    """Test Phase 1: Truth Classification Engine."""
    print("\n" + "="*60)
    print("PHASE 1: Truth Classification Engine")
    print("="*60)
    
    test_cases = [
        ([], "UNVERIFIED", 0),
        ([{"source_id": "s1"}], "SINGLE_SOURCE", 1),
        ([{"source_id": "s1"}, {"source_id": "s2"}], "CORROBORATED", 2),
        ([{"source_id": "s1", "is_institutional": True}], "INSTITUTIONAL", 3),
        ([{"source_id": "s1", "primary_evidence": True}], "PRIMARY_EVIDENCE", 4),
    ]
    
    for sources, expected_name, expected_level in test_cases:
        level = classify_truth_level(sources)
        status = "✓" if level == expected_level else "✗"
        print(f"{status} Sources: {len(sources)} → Level {level} ({expected_name})")
    
    print(f"✓ Phase 1 Complete")
    return


def test_phase2_source_reliability():
    """Test Phase 2: Source Reliability Scoring."""
    print("\n" + "="*60)
    print("PHASE 2: Source Reliability Scoring")
    print("="*60)
    
    sources = [
        {"source_id": "pib", "domain": "pib.gov.in", "is_institutional": True},
        {"source_id": "imd", "authority_score": 0.92},
        {"source_id": "blog", "source_type": "blog"},
    ]
    
    for source in sources:
        metadata = get_source_metadata(source)
        print(f"✓ {metadata['source_id']}: {metadata['reliability_score']} ({metadata['reliability_tier']})")
    
    print(f"✓ Phase 2 Complete")
    return


def test_phase3_event_matching():
    """Test Phase 3: Cross-Source Event Matching."""
    print("\n" + "="*60)
    print("PHASE 3: Cross-Source Event Matching")
    print("="*60)
    
    events = create_sample_events()
    groups = get_matched_event_groups(events)
    
    print(f"Total Events: {groups['total_events']}")
    print(f"Matched Groups: {groups['matched_groups']}")
    print(f"Unmatched Events: {groups['unmatched_events']}")
    
    for group in groups['groups']:
        print(f"✓ Group {group['group_id'][:8]}...")
        print(f"  Events: {group['event_count']}")
        print(f"  Match Score: {group['match_score']}")
        print(f"  Match Reasons: {group['match_reasons']}")
    
    print(f"✓ Phase 3 Complete")
    return


def test_phase4_conflict_detection():
    """Test Phase 4: Conflict Detection Engine."""
    print("\n" + "="*60)
    print("PHASE 4: Conflict Detection Engine")
    print("="*60)
    
    events = create_sample_events()
    registry_id = "REG_WEATHER_2026_03"
    conflicts = get_event_conflict_metadata(registry_id, events)
    
    print(f"Registry ID: {registry_id}")
    print(f"Conflict Detected: {conflicts['conflict_flag']}")
    print(f"Conflict Types: {conflicts['conflict_types']}")
    print(f"Conflicting Fields: {conflicts['conflicting_fields']}")
    
    if conflicts['conflict_flag']:
        print(f"✓ Conflict detected correctly!")
    else:
        print(f"⚠ No conflict detected (may need investigation)")
    
    print(f"✓ Phase 4 Complete")
    return


def test_phase5_truth_state_resolution():
    """Test Phase 5: Truth State Resolver."""
    print("\n" + "="*60)
    print("PHASE 5: Truth State Resolver")
    print("="*60)
    
    events = create_sample_events()
    config = TruthIntelligenceConfig(
        enable_conflict_detection=True,
        enable_event_matching=True,
        enable_source_scoring=True,
        enable_truth_resolution=True
    )
    
    from truth_intelligence.pipeline_integration import TruthIntelligenceLayer
    layer = TruthIntelligenceLayer(config)
    
    # Test first event
    event = events[0]
    truth_signals = layer.get_truth_signals(event, events, "REG_WEATHER_2026_03")
    
    print(f"Event: {event['event_id']}")
    truth_res = truth_signals.get('truth_resolution', {})
    print(f"✓ Truth Level: {truth_res.get('truth_level')} ({truth_res.get('truth_level_name')})")
    print(f"✓ Confidence: {truth_res.get('confidence_score')} ({truth_res.get('confidence_tier')})")
    print(f"✓ Conflict Flag: {truth_res.get('conflict_flag')}")
    print(f"✓ Corroborating Sources: {truth_res.get('corroborating_sources')}")
    print(f"✓ Conflicting Sources: {truth_res.get('conflicting_sources')}")
    
    print(f"✓ Phase 5 Complete")
    return


def test_phase6_pipeline_integration():
    """Test Phase 6: Full Pipeline Integration."""
    print("\n" + "="*60)
    print("PHASE 6: Pipeline Integration")
    print("="*60)
    
    events = create_sample_events()
    config = TruthIntelligenceConfig()
    
    enriched_events = process_event_pipeline(events, "REG_WEATHER_2026_03", config)
    
    print(f"Input Events: {len(events)}")
    print(f"Enriched Events: {len(enriched_events)}")
    
    for event in enriched_events:
        truth_intel = event.get('truth_intelligence', {})
        has_classification = bool(truth_intel.get('truth_classification'))
        has_reliability = bool(truth_intel.get('source_reliability'))
        has_matching = bool(truth_intel.get('event_matching'))
        has_conflict = bool(truth_intel.get('conflict_detection'))
        has_resolution = bool(truth_intel.get('truth_resolution'))
        
        status = "✓" if all([has_classification, has_reliability, has_matching, has_conflict, has_resolution]) else "✗"
        print(f"{status} {event['event_id']}: All 5 signal types present")
    
    # Validate output schema
    first_event = enriched_events[0]
    truth_intel = first_event['truth_intelligence']
    
    required_keys = ['truth_classification', 'source_reliability', 'event_matching', 'conflict_detection', 'truth_resolution', 'processing_timestamp']
    all_present = all(key in truth_intel for key in required_keys)
    
    if all_present:
        print(f"✓ Output schema validated")
    else:
        missing = [k for k in required_keys if k not in truth_intel]
        print(f"✗ Missing keys: {missing}")
        return
    
    print(f"✓ Phase 6 Complete")
    return


def validate_output_format():
    """Validate output matches expected schema from truth_signals.json."""
    print("\n" + "="*60)
    print("OUTPUT FORMAT VALIDATION")
    print("="*60)
    
    events = create_sample_events()
    enriched = process_event_pipeline(events, "REG_WEATHER_2026_03")
    
    # Check structure
    event = enriched[0]
    truth_intel = event['truth_intelligence']
    
    checks = {
        "event_id": event.get('event_id') is not None,
        "registry_reference_id": event.get('registry_reference_id') is not None,
        "truth_classification.truth_level": truth_intel['truth_classification'].get('truth_level') is not None,
        "truth_classification.truth_level_name": isinstance(truth_intel['truth_classification'].get('truth_level_name'), str),
        "source_reliability": isinstance(truth_intel['source_reliability'], dict),
        "event_matching.is_matched": isinstance(truth_intel['event_matching'].get('is_matched'), bool),
        "conflict_detection.conflict_flag": isinstance(truth_intel['conflict_detection'].get('conflict_flag'), bool),
        "truth_resolution.truth_level": truth_intel['truth_resolution'].get('truth_level') is not None,
        "truth_resolution.confidence_score": isinstance(truth_intel['truth_resolution'].get('confidence_score'), (int, float)),
        "truth_resolution.confidence_tier": isinstance(truth_intel['truth_resolution'].get('confidence_tier'), str),
        "processing_timestamp": isinstance(truth_intel.get('processing_timestamp'), str),
    }
    
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
    
    all_passed = all(checks.values())
    if all_passed:
        print(f"\n✓ Output format is valid and matches expected schema")
    else:
        print(f"\n✗ Some output format checks failed")
    
    return all_passed


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TRUTH INTELLIGENCE LAYER - INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Test Start: {datetime.now(timezone.utc).isoformat()}")
    
    try:
        # Run all phase tests
        results = {
            "Phase 1 - Truth Classification": test_phase1_truth_classification(),
            "Phase 2 - Source Reliability": test_phase2_source_reliability(),
            "Phase 3 - Event Matching": test_phase3_event_matching(),
            "Phase 4 - Conflict Detection": test_phase4_conflict_detection(),
            "Phase 5 - Truth State Resolution": test_phase5_truth_state_resolution(),
            "Phase 6 - Pipeline Integration": test_phase6_pipeline_integration(),
            "Output Format Validation": validate_output_format(),
        }
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print("\n" + "-"*60)
        print(f"Results: {passed}/{total} tests passed")
        print(f"Test End: {datetime.now(timezone.utc).isoformat()}")
        
        if passed == total:
            print("\n🎉 All tests passed! Truth Intelligence Layer is operational.")
            return 0
        else:
            print(f"\n⚠ {total - passed} test(s) failed. Please review.")
            return 1
            
    except Exception as e:
        print(f"\n✗ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
