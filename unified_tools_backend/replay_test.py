"""
Replay Determinism Test
Verifies that the ingestion pipeline produces identical outputs for identical inputs.
Core guarantee: Replay produces same event_id, truth_level, conflict_flag.
"""

import json
from typing import List, Dict, Any
from datetime import datetime

# Import ingestion pipeline
from ingestion_pipeline import IngestionPipeline


class ReplayTest:
    """
    Tests determinism by running same inputs multiple times.
    
    Guarantees:
    - Same input → same output (deterministic)
    - Fully replayable
    - No randomness
    """
    
    def __init__(self, num_replays: int = 3):
        """
        Initialize replay tester.
        
        Args:
            num_replays: Number of times to replay (default 3)
        """
        self.num_replays = num_replays
        self.test_results: List[Dict[str, Any]] = []
    
    def test_single_event_determinism(
        self,
        source_url: str,
        raw_content: str,
        registry_reference_id: str,
        location: str = "India"
    ) -> Dict[str, Any]:
        """
        Test that same event produces identical outputs.
        
        Args:
            source_url: Source URL
            raw_content: Raw content
            registry_reference_id: Registry ID
            location: Location
            
        Returns:
            Test result dictionary
        """
        print(f"\n{'='*60}")
        print(f"Testing Single Event Determinism ({self.num_replays} replays)")
        print(f"{'='*60}")
        
        results = []
        
        for i in range(self.num_replays):
            pipeline = IngestionPipeline()
            success, record, error = pipeline.ingest_event(
                source_url=source_url,
                raw_content=raw_content,
                registry_reference_id=registry_reference_id,
                location=location
            )
            
            if not success:
                return {
                    "test_name": "single_event_determinism",
                    "passed": False,
                    "error": f"Ingestion failed on replay {i+1}: {error}"
                }
            
            results.append(record)
            print(f"Replay {i+1}:")
            print(f"  Event ID:      {record['event_id'][:24]}...")
            print(f"  Truth Level:   {record['truth_level']}")
            print(f"  Conflict Flag: {record['conflict_flag']}")
        
        # Verify all replays produce identical outputs
        event_ids = [r['event_id'] for r in results]
        truth_levels = [r['truth_level'] for r in results]
        conflict_flags = [r['conflict_flag'] for r in results]
        
        event_ids_match = len(set(event_ids)) == 1
        truth_levels_match = len(set(truth_levels)) == 1
        conflict_flags_match = len(set(conflict_flags)) == 1
        
        all_match = event_ids_match and truth_levels_match and conflict_flags_match
        
        print(f"\nDeterminism Verification:")
        print(f"  Event IDs Match:      {'✓ YES' if event_ids_match else '✗ NO'}")
        print(f"  Truth Levels Match:   {'✓ YES' if truth_levels_match else '✗ NO'}")
        print(f"  Conflict Flags Match: {'✓ YES' if conflict_flags_match else '✗ NO'}")
        
        test_result = {
            "test_name": "single_event_determinism",
            "passed": all_match,
            "num_replays": self.num_replays,
            "event_ids_match": event_ids_match,
            "truth_levels_match": truth_levels_match,
            "conflict_flags_match": conflict_flags_match,
            "canonical_event_id": event_ids[0] if event_ids_match else None,
            "canonical_truth_level": truth_levels[0] if truth_levels_match else None,
            "canonical_conflict_flag": conflict_flags[0] if conflict_flags_match else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.test_results.append(test_result)
        return test_result
    
    def test_batch_determinism(
        self,
        events: List[Dict[str, str]],
        num_events: int = 5
    ) -> Dict[str, Any]:
        """
        Test determinism with a batch of events.
        
        Args:
            events: Event input list
            num_events: Number of events to test
            
        Returns:
            Test result dictionary
        """
        print(f"\n{'='*60}")
        print(f"Testing Batch Determinism ({num_events} events x {self.num_replays} replays)")
        print(f"{'='*60}")
        
        batch_runs = []
        
        for run in range(self.num_replays):
            pipeline = IngestionPipeline()
            total_success = 0
            total_failed = 0
            run_results = []
            
            for event in events[:num_events]:
                success, record, error = pipeline.ingest_event(
                    source_url=event.get("source_url"),
                    raw_content=event.get("raw_content"),
                    registry_reference_id=event.get("registry_reference_id"),
                    location=event.get("location", "India")
                )
                
                if success:
                    total_success += 1
                    run_results.append({
                        "event_id": record['event_id'],
                        "truth_level": record['truth_level']
                    })
                else:
                    total_failed += 1
            
            batch_runs.append(run_results)
            print(f"Run {run+1}: {total_success} successful, {total_failed} failed")
        
        # Compare batches
        all_match = True
        if len(batch_runs) > 1:
            first_run = batch_runs[0]
            for i, run in enumerate(batch_runs[1:], start=2):
                if len(run) != len(first_run):
                    all_match = False
                    print(f"  ✗ Run {i} has different number of events")
                
                for j, (expected, actual) in enumerate(zip(first_run, run)):
                    if expected['event_id'] != actual['event_id']:
                        all_match = False
                        print(f"  ✗ Event {j} has different event_id in run {i}")
                    if expected['truth_level'] != actual['truth_level']:
                        all_match = False
                        print(f"  ✗ Event {j} has different truth_level in run {i}")
        
        if all_match:
            print(f"\n✓ All batch runs produced identical results")
        
        test_result = {
            "test_name": "batch_determinism",
            "passed": all_match,
            "num_events": num_events,
            "num_replays": self.num_replays,
            "total_events_per_run": len(batch_runs[0]) if batch_runs else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.test_results.append(test_result)
        return test_result
    
    def get_test_report(self) -> Dict[str, Any]:
        """Get comprehensive test report."""
        passed_tests = sum(1 for r in self.test_results if r.get("passed"))
        total_tests = len(self.test_results)
        
        return {
            "test_suite": "replay_determinism",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "all_passed": passed_tests == total_tests,
            "results": self.test_results,
            "timestamp": datetime.utcnow().isoformat()
        }


def run_replay_tests():
    """Run comprehensive replay determinism tests."""
    print("\n" + "🔄 "*20)
    print("TRUTH INTELLIGENCE INGESTION PIPELINE - DETERMINISM TEST SUITE")
    print("🔄 "*20)
    
    tester = ReplayTest(num_replays=3)
    
    # Test 1: Single event determinism
    test1_result = tester.test_single_event_determinism(
        source_url="https://example.com/news/weather",
        raw_content="IMD predicts normal monsoon in 2026. Rainfall expected to be normal.",
        registry_reference_id="REG_WEATHER_2026_03",
        location="India"
    )
    
    # Test 2: Batch determinism
    batch_events = [
        {
            "source_url": f"https://source{i}.com/news/{i}",
            "raw_content": f"News event {i} with deterministic content",
            "registry_reference_id": f"REG_TEST_2026_0{i}",
            "location": ["India", "US", "China", "UK", "Japan"][i % 5]
        }
        for i in range(1, 6)
    ]
    
    test2_result = tester.test_batch_determinism(batch_events, num_events=5)
    
    # Summary
    print(f"\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    report = tester.get_test_report()
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed_tests']}")
    print(f"Failed: {report['failed_tests']}")
    print(f"All Passed: {'✓ YES' if report['all_passed'] else '✗ NO'}")
    
    if report['all_passed']:
        print(f"\n🎉 DETERMINISM GUARANTEE VERIFIED")
        print(f"   Pipeline is fully replayable and deterministic")
    else:
        print(f"\n❌ DETERMINISM TEST FAILED")
        print(f"   Pipeline has non-deterministic behavior")
    
    # Return report
    return report


if __name__ == "__main__":
    report = run_replay_tests()
    print(f"\nTest Report: {json.dumps(report, indent=2)}")
