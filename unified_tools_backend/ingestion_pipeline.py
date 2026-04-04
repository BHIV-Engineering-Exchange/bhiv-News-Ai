"""
Truth Intelligence Ingestion Pipeline
Orchestrates all phases for deterministic, schema-valid event ingestion.

Flow:
  raw_input
    ↓
  source_hash_generation (Phase 3)
    ↓
  schema_validation (Phase 2)
    ↓
  geo_normalization (Phase 5)
    ↓
  truth_classification (integrated)
    ↓
  conflict_detection (integrated)
    ↓
  event_id_generation (Phase 4)
    ↓
  final_output (schema-valid, intelligence-ready)
"""

import json
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Import pipeline components
from source_hash_generator import generate_source_hash, SourceHashGenerator
from event_id_generator import generate_event_id, EventIDGenerator
from geo_normalizer import normalize_location, GeoNormalizer
from validate_ingestion_contract import validate_ingestion_record, IngestionContractValidator

# Import monitoring
try:
    from monitor_backend import record_ingestion, get_monitor_report
except ImportError:
    # Fallback if monitor not available
    def record_ingestion(*args, **kwargs): pass
    def get_monitor_report(): return {}

# Import Truth Intelligence modules (mandatory integration; no fallback logic)
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from truth_intelligence.truth_classifier import classify_truth_level
from truth_intelligence.conflict_detector import detect_conflicts


class IngestionPipeline:
    """
    Main orchestrator for deterministic event ingestion.
    
    Guarantees:
    - Deterministic output (replayable)
    - Schema-valid events
    - Fully integrated truth signals
    - No randomness or side effects
    """
    
    def __init__(self):
        """Initialize pipeline components."""
        self.hash_generator = SourceHashGenerator()
        self.event_id_generator = EventIDGenerator()
        self.geo_normalizer = GeoNormalizer()
        self.validator = IngestionContractValidator()
        self.processed_events: List[Dict[str, Any]] = []
        self.ingestion_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
    
    def ingest_event(
        self,
        source_url: str,
        raw_content: str,
        registry_reference_id: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        location: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Ingest a single event through the full pipeline.
        
        Args:
            source_url: Source URL
            raw_content: Raw content from source
            registry_reference_id: Registry ID for grouping
            sources: Source metadata for truth classification
            location: Location text for geo normalization
            
        Returns:
            Tuple of (success, event_dict, error_message)
        """
        self.ingestion_stats["total_processed"] += 1
        event_id = None
        truth_level = None
        conflict_flag = False
        geo_resolved = False
        stage = "input_validation"
        
        try:
            if not source_url or not isinstance(source_url, str):
                raise ValueError("source_url must be a non-empty string")
            if not raw_content or not isinstance(raw_content, str):
                raise ValueError("raw_content must be a non-empty string")
            if not registry_reference_id or not isinstance(registry_reference_id, str):
                raise ValueError("registry_reference_id must be a non-empty string")

            # Phase 3: Source Hash Generation (BEFORE parsing)
            stage = "source_hash_generation"
            source_hash = self.hash_generator.generate_source_hash(raw_content)
            
            # Phase 5: Geo Normalization
            stage = "geo_normalization"
            geo_normalized = self.geo_normalizer.normalize_location(location)
            geo_resolved = geo_normalized is not None
            
            # Prepare sources for truth classification
            if sources is None:
                sources = [{"source_url": source_url, "is_institutional": False}]
            
            # Integrated Truth Classification
            stage = "truth_classification"
            truth_level = classify_truth_level(sources)
            
            # Phase 4: Event ID Generation (deterministic)
            stage = "event_id_generation"
            event_id = self.event_id_generator.generate_event_id(
                source_hash,
                registry_reference_id
            )
            
            # Ingestion timestamp
            ingestion_timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Integrated Conflict Detection
            stage = "conflict_detection"
            registry_events = [
                e for e in self.processed_events
                if e.get("registry_reference_id") == registry_reference_id
            ]
            temp_event = {
                "event_id": event_id,
                "registry_reference_id": registry_reference_id,
                "prediction": None
            }
            conflict_flag = detect_conflicts(registry_reference_id, registry_events + [temp_event])
            
            # Build final event record
            event_record = {
                "event_id": event_id,
                "source_url": source_url,
                "source_hash": source_hash,
                "ingestion_timestamp": ingestion_timestamp,
                "raw_content": raw_content,
                "truth_level": truth_level,
                "conflict_flag": conflict_flag,
                "registry_reference_id": registry_reference_id,
                "geo_normalized": geo_normalized
            }
            
            # Phase 2: Schema Validation
            stage = "schema_validation"
            is_valid, error_msg = validate_ingestion_record(event_record)
            if not is_valid:
                raise ValueError(f"Schema validation failed: {error_msg}")

            standardized_output = {
                "event_id": event_record["event_id"],
                "source_hash": event_record["source_hash"],
                "truth_level": event_record["truth_level"],
                "conflict_flag": event_record["conflict_flag"],
                "geo_normalized": event_record["geo_normalized"],
                "registry_reference_id": event_record["registry_reference_id"]
            }
            
            # Event successfully ingested
            self.processed_events.append(event_record)
            self.ingestion_stats["successful"] += 1
            
            # Record monitoring
            record_ingestion(
                success=True,
                event_id=event_id,
                truth_level=truth_level,
                conflict=conflict_flag,
                geo_resolved=geo_resolved,
                schema_validated=True
            )
            
            return True, standardized_output, None
            
        except Exception as e:
            self.ingestion_stats["failed"] += 1
            error_msg = str(e)
            self.ingestion_stats["errors"].append({
                "registry_reference_id": registry_reference_id,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Record failure
            failure_type = {
                "schema_validation": "schema_validation",
                "truth_classification": "classification",
                "conflict_detection": "conflict_detection"
            }.get(stage, "ingestion")

            record_ingestion(
                success=False,
                event_id=event_id or "",
                error=error_msg,
                truth_level=truth_level,
                conflict=conflict_flag,
                geo_resolved=geo_resolved,
                failure_type=failure_type,
                schema_validated=(stage == "schema_validation")
            )
            
            return False, None, error_msg
    
    def ingest_batch(
        self,
        events: List[Dict[str, str]]
    ) -> Tuple[int, int, List[Dict[str, Any]]]:
        """
        Ingest a batch of events.
        
        Args:
            events: List of event dictionaries with keys:
                - source_url
                - raw_content
                - registry_reference_id
                - location (optional)
                - sources (optional)
                
        Returns:
            Tuple of (successful, failed, results)
        """
        results = []
        successful = 0
        failed = 0
        
        for event_input in events:
            success, record, error = self.ingest_event(
                source_url=event_input.get("source_url"),
                raw_content=event_input.get("raw_content"),
                registry_reference_id=event_input.get("registry_reference_id"),
                sources=event_input.get("sources"),
                location=event_input.get("location")
            )
            
            if success:
                results.append(record)
                successful += 1
            else:
                results.append({"error": error})
                failed += 1
        
        return successful, failed, results
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return {
            **self.ingestion_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_processed_events(self) -> List[Dict[str, Any]]:
        """Get all successfully processed events."""
        return self.processed_events
    
    def clear(self) -> None:
        """Reset pipeline state."""
        self.processed_events = []
        self.ingestion_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }


# Singleton instance
_pipeline = None


def get_pipeline() -> IngestionPipeline:
    """Get or create global pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = IngestionPipeline()
    return _pipeline


def ingest_event(
    source_url: str,
    raw_content: str,
    registry_reference_id: str,
    sources: Optional[List[Dict[str, Any]]] = None,
    location: Optional[str] = None
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Ingest a single event.
    Convenience function.
    """
    pipeline = get_pipeline()
    return pipeline.ingest_event(source_url, raw_content, registry_reference_id, sources, location)


def ingest_batch(
    events: List[Dict[str, str]]
) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Ingest a batch of events.
    Convenience function.
    """
    pipeline = get_pipeline()
    return pipeline.ingest_batch(events)


def get_pipeline_stats() -> Dict[str, Any]:
    """Get pipeline statistics."""
    pipeline = get_pipeline()
    return pipeline.get_ingestion_stats()


def get_processed_events() -> List[Dict[str, Any]]:
    """Get processed events."""
    pipeline = get_pipeline()
    return pipeline.get_processed_events()


def clear_pipeline() -> None:
    """Clear pipeline."""
    pipeline = get_pipeline()
    pipeline.clear()


def test_ingestion_pipeline():
    """Test full ingestion pipeline."""
    print("Testing deterministic ingestion pipeline...")
    
    pipeline = IngestionPipeline()
    
    # Test event
    event_input = {
        "source_url": "https://example.com/news/weather",
        "raw_content": "IMD predicts normal monsoon in 2026",
        "registry_reference_id": "REG_WEATHER_2026_03",
        "location": "India",
        "sources": [
            {"source_id": "imd", "is_institutional": True, "authority_score": 0.92}
        ]
    }
    
    # Process event
    success, record, error = pipeline.ingest_event(**event_input)
    
    if success:
        print(f"✓ PASS: Event ingested successfully")
        print(f"  Event ID: {record['event_id'][:16]}...")
        print(f"  Truth Level: {record['truth_level']}")
        print(f"  Conflict Flag: {record['conflict_flag']}")
        print(f"  Geo (Country): {record['geo_normalized'].get('country_code') if record['geo_normalized'] else None}")
    else:
        print(f"✗ FAIL: Ingestion failed - {error}")
    
    # Test determinism - ingest same event again
    success2, record2, error2 = pipeline.ingest_event(**event_input)
    
    if success2 and record["event_id"] == record2["event_id"]:
        print(f"✓ PASS: Deterministic event_id")
    else:
        print(f"✗ FAIL: Event IDs don't match (non-deterministic)")
    
    # Get stats
    stats = pipeline.get_ingestion_stats()
    print(f"\n  Pipeline Stats:")
    print(f"    Total Processed: {stats['total_processed']}")
    print(f"    Successful: {stats['successful']}")
    print(f"    Failed: {stats['failed']}")


if __name__ == "__main__":
    test_ingestion_pipeline()
