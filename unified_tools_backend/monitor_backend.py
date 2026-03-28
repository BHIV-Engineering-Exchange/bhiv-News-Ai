"""
Monitor Backend - Ingestion Pipeline Health Monitoring
Tracks ingestion success rate, schema failures, classification failures.
Produces monitor_report.json with health metrics.
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path


class IngestionMonitor:
    """
    Monitors Truth Intelligence ingestion pipeline health.
    
    Tracks:
    - Ingestion success rate
    - Schema validation failures
    - Classification failures
    - Conflict detection failures
    - Geo normalization effectiveness
    """
    
    def __init__(self, report_path: str = "monitor_report.json"):
        """
        Initialize monitor.
        
        Args:
            report_path: Path to write monitor report
        """
        self.report_path = report_path
        self.metrics = {
            "ingestion_health": {
                "total_ingested": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0
            },
            "schema_validation": {
                "total_validated": 0,
                "passed": 0,
                "failed": 0,
                "failure_reasons": {}
            },
            "truth_classification": {
                "total_classified": 0,
                "level_distribution": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0},
                "failures": 0
            },
            "conflict_detection": {
                "total_checked": 0,
                "conflicts_found": 0,
                "conflicts_rate": 0.0,
                "failures": 0
            },
            "geo_normalization": {
                "total_normalized": 0,
                "resolved": 0,
                "null_resolution": 0,
                "resolution_rate": 0.0
            },
            "event_timestamps": {
                "first_event": None,
                "last_event": None,
                "events_per_minute": 0.0
            }
        }
        self.event_log: List[Dict[str, Any]] = []
    
    def record_ingestion(
        self,
        success: bool,
        event_id: str = "",
        error: str = "",
        truth_level: int = None,
        conflict: bool = False,
        geo_resolved: bool = False
    ) -> None:
        """
        Record an ingestion event.
        
        Args:
            success: Whether ingestion succeeded
            event_id: Event ID
            error: Error message if failed
            truth_level: Truth classification level
            conflict: Conflict detected
            geo_resolved: Geo normalization resolved
        """
        self.metrics["ingestion_health"]["total_ingested"] += 1
        
        if success:
            self.metrics["ingestion_health"]["successful"] += 1
        else:
            self.metrics["ingestion_health"]["failed"] += 1
            if error:
                self.metrics["schema_validation"]["failure_reasons"][error] = \
                    self.metrics["schema_validation"]["failure_reasons"].get(error, 0) + 1
        
        # Track truth classification
        if truth_level is not None:
            self.metrics["truth_classification"]["total_classified"] += 1
            if truth_level in self.metrics["truth_classification"]["level_distribution"]:
                self.metrics["truth_classification"]["level_distribution"][truth_level] += 1
        
        # Track conflict detection
        self.metrics["conflict_detection"]["total_checked"] += 1
        if conflict:
            self.metrics["conflict_detection"]["conflicts_found"] += 1
        
        # Track geo normalization
        self.metrics["geo_normalization"]["total_normalized"] += 1
        if geo_resolved:
            self.metrics["geo_normalization"]["resolved"] += 1
        else:
            self.metrics["geo_normalization"]["null_resolution"] += 1
        
        # Update rates
        self._update_rates()
        
        # Log event
        self.event_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": event_id,
            "success": success,
            "truth_level": truth_level,
            "conflict": conflict,
            "geo_resolved": geo_resolved,
            "error": error
        })
        
        # Update first/last event time
        if not self.metrics["event_timestamps"]["first_event"]:
            self.metrics["event_timestamps"]["first_event"] = datetime.utcnow().isoformat()
        self.metrics["event_timestamps"]["last_event"] = datetime.utcnow().isoformat()
    
    def _update_rates(self) -> None:
        """Update calculated rates."""
        # Success rate
        total = self.metrics["ingestion_health"]["total_ingested"]
        if total > 0:
            self.metrics["ingestion_health"]["success_rate"] = \
                self.metrics["ingestion_health"]["successful"] / total
        
        # Conflict rate
        total_conflicts = self.metrics["conflict_detection"]["total_checked"]
        if total_conflicts > 0:
            self.metrics["conflict_detection"]["conflicts_rate"] = \
                self.metrics["conflict_detection"]["conflicts_found"] / total_conflicts
        
        # Geo resolution rate
        total_geo = self.metrics["geo_normalization"]["total_normalized"]
        if total_geo > 0:
            self.metrics["geo_normalization"]["resolution_rate"] = \
                self.metrics["geo_normalization"]["resolved"] / total_geo
    
    def get_health_status(self) -> str:
        """
        Get overall health status.
        
        Returns:
            HEALTHY, DEGRADED, or CRITICAL
        """
        success_rate = self.metrics["ingestion_health"]["success_rate"]
        
        if success_rate >= 0.95:
            return "HEALTHY"
        elif success_rate >= 0.80:
            return "DEGRADED"
        else:
            return "CRITICAL"
    
    def write_report(self, output_path: str = None) -> str:
        """
        Write monitoring report to JSON file.
        
        Args:
            output_path: Path to write report (default: monitor_report.json)
            
        Returns:
            Path to written report
        """
        output_path = output_path or self.report_path
        
        report = {
            "monitor_report": {
                "generated_at": datetime.utcnow().isoformat(),
                "health_status": self.get_health_status(),
                "metrics": self.metrics,
                "summary": {
                    "total_ingested": self.metrics["ingestion_health"]["total_ingested"],
                    "success_rate": f"{self.metrics['ingestion_health']['success_rate']:.2%}",
                    "conflict_rate": f"{self.metrics['conflict_detection']['conflicts_rate']:.2%}",
                    "geo_resolution_rate": f"{self.metrics['geo_normalization']['resolution_rate']:.2%}",
                    "truth_level_distribution": self.metrics["truth_classification"]["level_distribution"]
                }
            }
        }
        
        # Write to file
        output_dir = os.path.dirname(output_path) or "."
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_path
    
    def get_report_dict(self) -> Dict[str, Any]:
        """Get monitor report as dictionary."""
        return {
            "monitor_report": {
                "generated_at": datetime.utcnow().isoformat(),
                "health_status": self.get_health_status(),
                "metrics": self.metrics
            }
        }


# Singleton instance
_monitor = None


def get_monitor() -> IngestionMonitor:
    """Get or create global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = IngestionMonitor()
    return _monitor


def record_ingestion(
    success: bool,
    event_id: str = "",
    error: str = "",
    truth_level: int = None,
    conflict: bool = False,
    geo_resolved: bool = False
) -> None:
    """
    Record ingestion event.
    Convenience function.
    """
    monitor = get_monitor()
    monitor.record_ingestion(success, event_id, error, truth_level, conflict, geo_resolved)


def get_health_status() -> str:
    """Get system health status."""
    monitor = get_monitor()
    return monitor.get_health_status()


def write_monitor_report(output_path: str = "monitor_report.json") -> str:
    """Write monitor report."""
    monitor = get_monitor()
    return monitor.write_report(output_path)


def get_monitor_report() -> Dict[str, Any]:
    """Get monitor report."""
    monitor = get_monitor()
    return monitor.get_report_dict()


def test_monitor():
    """Test monitoring functionality."""
    print("Testing ingestion monitor...")
    
    monitor = IngestionMonitor()
    
    # Simulate ingestion events
    test_events = [
        (True, "evt_001", "", 3, False, True),
        (True, "evt_002", "", 2, True, True),
        (False, "evt_003", "Schema validation failed", None, False, False),
        (True, "evt_004", "", 4, False, True),
        (True, "evt_005", "", 3, False, True),
    ]
    
    for success, event_id, error, truth_level, conflict, geo_resolved in test_events:
        monitor.record_ingestion(success, event_id, error, truth_level, conflict, geo_resolved)
    
    # Get report
    report = monitor.get_report_dict()
    
    print(f"Health Status: {report['monitor_report']['health_status']}")
    print(f"Total Ingested: {report['monitor_report']['metrics']['ingestion_health']['total_ingested']}")
    print(f"Success Rate: {report['monitor_report']['metrics']['ingestion_health']['success_rate']:.2%}")
    print(f"Conflict Rate: {report['monitor_report']['metrics']['conflict_detection']['conflicts_rate']:.2%}")
    print(f"Geo Resolution Rate: {report['monitor_report']['metrics']['geo_normalization']['resolution_rate']:.2%}")
    
    # Write report
    path = monitor.write_report("test_monitor_report.json")
    print(f"\nReport written to: {path}")


if __name__ == "__main__":
    test_monitor()
