#!/usr/bin/env python3
"""
Monitor Backend - Real-time Health & Error Tracking
========================================================
Monitors News AI backend for:
- Availability (reachability)
- Latency measurements
- Endpoint health
- Error capture & logging

Run: python monitor_backend.py
Logs: newsai_error_log.json (append-only)
Interval: 30 seconds

Status codes:
✓ HEALTHY - All endpoints respond within SLA
⚠ DEGRADED - Some endpoints slow or failing
✗ CRITICAL - Backend unreachable or multiple failures
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple
import threading
from pathlib import Path

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MONITOR_INTERVAL = 30  # seconds
ERROR_LOG_FILE = "newsai_error_log.json"
LATENCY_THRESHOLD_MS = 2000  # ms - anything slower is flagged
TIMEOUT_SECONDS = 10

# Key endpoints to monitor
CRITICAL_ENDPOINTS = [
    ("/", "GET", "Root endpoint"),
    ("/health", "GET", "Health check"),
]

OPERATIONAL_ENDPOINTS = [
    ("/api/unified-news-workflow", "POST", "Main pipeline"),
    ("/api/scrape", "POST", "Scraping service"),
    ("/api/summarize", "POST", "Summarization service"),
    ("/api/vet", "POST", "Authenticity vetting"),
]

# Test payloads
TEST_PAYLOADS = {
    "/api/unified-news-workflow": {"url": "https://example.com"},
    "/api/scrape": {"url": "https://example.com"},
    "/api/summarize": {"text": "Sample news article for testing."},
    "/api/vet": {"url": "https://example.com", "headline": "Test", "source": "test"},
}


class NewsAIMonitor:
    """Backend health monitoring and error logging system."""

    def __init__(self, backend_url: str = BACKEND_URL, monitor_interval: int = MONITOR_INTERVAL, error_log_file: str = ERROR_LOG_FILE):
        self.start_time = datetime.now()
        self.health_history: List[Dict[str, Any]] = []
        self.error_history: List[Dict[str, Any]] = []
        self.request_count = 0
        self.error_count = 0
        self.running = True
        self.backend_url = backend_url
        self.monitor_interval = monitor_interval
        self.error_log_file = error_log_file

    def log_error(self, endpoint: str, error: str, status_code: int = None, latency_ms: float = None):
        """Append error to newsai_error_log.json (append-only)."""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "error": error,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "backend_url": self.backend_url,
        }

        # Read existing errors
        errors = []
        if os.path.exists(self.error_log_file):
            try:
                with open(self.error_log_file, "r") as f:
                    content = f.read().strip()
                    if content:
                        errors = json.loads(content)
            except Exception as e:
                print(f"⚠ Error reading error log: {e}")

        # Append new error
        errors.append(error_entry)
        self.error_history.append(error_entry)
        self.error_count += 1

        # Save back
        try:
            with open(self.error_log_file, "w") as f:
                json.dump(errors, f, indent=2)
        except Exception as e:
            print(f"✗ Failed to write error log: {e}")

    def check_endpoint(self, endpoint: str, method: str, description: str, payload: Dict = None) -> Tuple[bool, float, int, str]:
        """
        Check if an endpoint is healthy.
        
        Returns: (is_healthy, latency_ms, status_code, error_message)
        """
        url = f"{self.backend_url}{endpoint}"
        start = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=TIMEOUT_SECONDS)
            else:  # POST
                response = requests.post(url, json=payload or {}, timeout=TIMEOUT_SECONDS)
            
            latency_ms = (time.time() - start) * 1000
            self.request_count += 1

            if response.status_code == 200:
                if latency_ms > LATENCY_THRESHOLD_MS:
                    return False, latency_ms, 200, f"Latency {latency_ms:.0f}ms exceeds threshold {LATENCY_THRESHOLD_MS}ms"
                return True, latency_ms, 200, ""

            # Non-200 response
            return False, latency_ms, response.status_code, f"HTTP {response.status_code}: {response.text[:100]}"

        except requests.exceptions.Timeout:
            latency_ms = (time.time() - start) * 1000
            return False, latency_ms, None, "Request timeout"
        except requests.exceptions.ConnectionError:
            latency_ms = (time.time() - start) * 1000
            return False, latency_ms, None, "Connection refused"
        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            return False, latency_ms, None, str(e)

    def run_health_check(self) -> Dict[str, Any]:
        """Full health check of all monitored endpoints."""
        check_result = {
            "timestamp": datetime.now().isoformat(),
            "backend_url": self.backend_url,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "critical_checks": [],
            "operational_checks": [],
            "status": "UNKNOWN",
            "summary": "",
        }

        critical_healthy = 0
        critical_total = len(CRITICAL_ENDPOINTS)

        # Check critical endpoints
        print("\n[CRITICAL ENDPOINTS]")
        for endpoint, method, description in CRITICAL_ENDPOINTS:
            is_healthy, latency, status_code, error_msg = self.check_endpoint(endpoint, method, description)

            check = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "healthy": is_healthy,
                "latency_ms": round(latency, 2),
                "status_code": status_code,
            }
            check_result["critical_checks"].append(check)

            if is_healthy:
                critical_healthy += 1
                status_icon = "[OK]"
            else:
                status_icon = "[FAIL]"
                self.log_error(endpoint, error_msg, status_code, latency)

            print(f"{status_icon} {endpoint} ({description}): {latency:.0f}ms")
            if not is_healthy:
                print(f"   └─ {error_msg}")

        # Check operational endpoints (with test payloads)
        print("\n[OPERATIONAL ENDPOINTS]")
        operational_healthy = 0
        operational_total = len(OPERATIONAL_ENDPOINTS)

        for endpoint, method, description in OPERATIONAL_ENDPOINTS:
            payload = TEST_PAYLOADS.get(endpoint)
            is_healthy, latency, status_code, error_msg = self.check_endpoint(
                endpoint, method, description, payload
            )

            check = {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "healthy": is_healthy,
                "latency_ms": round(latency, 2),
                "status_code": status_code,
            }
            check_result["operational_checks"].append(check)

            if is_healthy:
                operational_healthy += 1
                status_icon = "[OK]"
            else:
                status_icon = "[WARN]"
                self.log_error(endpoint, error_msg, status_code, latency)

            print(f"{status_icon} {endpoint} ({description}): {latency:.0f}ms")
            if not is_healthy:
                print(f"   └─ {error_msg}")

        # Determine overall status
        if critical_healthy == critical_total and operational_healthy == operational_total:
            check_result["status"] = "HEALTHY"
            status_icon = "[OK]"
        elif critical_healthy == critical_total:
            check_result["status"] = "DEGRADED"
            status_icon = "[WARN]"
        else:
            check_result["status"] = "CRITICAL"
            status_icon = "[FAIL]"

        check_result["summary"] = (
            f"{status_icon} Overall Status: {check_result['status']} | "
            f"Critical: {critical_healthy}/{critical_total} | "
            f"Operational: {operational_healthy}/{operational_total} | "
            f"Errors logged: {self.error_count}"
        )

        self.health_history.append(check_result)
        return check_result

    def display_summary(self, check_result: Dict[str, Any]):
        """Display monitoring summary."""
        print("\n" + "=" * 70)
        print(f"  {check_result['summary']}")
        print("=" * 70)

    def monitor_loop(self, max_iterations: int = None):
        """Main monitoring loop."""
        iteration = 0
        
        print(f"\n{'='*70}")
        print(f"  🕳️ NEWS AI BACKEND MONITOR")
        print(f"  Backend: {self.backend_url}")
        print(f"  Interval: {self.monitor_interval}s")
        print(f"  Started: {datetime.now().isoformat()}")
        print(f"{'='*70}")

        try:
            while self.running:
                if max_iterations and iteration >= max_iterations:
                    break

                check_result = self.run_health_check()
                self.display_summary(check_result)

                iteration += 1

                if max_iterations is None:
                    # Continuous monitoring
                    time.sleep(self.monitor_interval)
                else:
                    # Test mode - don't sleep after last iteration
                    if iteration < max_iterations:
                        time.sleep(self.monitor_interval)

        except KeyboardInterrupt:
            print("\n\n✓ Monitor stopped by user.")
            self.running = False

    def generate_report(self) -> Dict[str, Any]:
        """Generate monitoring report."""
        return {
            "report_generated": datetime.now().isoformat(),
            "backend_url": self.backend_url,
            "total_checks": len(self.health_history),
            "total_errors": self.error_count,
            "total_requests": self.request_count,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "status_distribution": {
                "HEALTHY": len([h for h in self.health_history if h["status"] == "HEALTHY"]),
                "DEGRADED": len([h for h in self.health_history if h["status"] == "DEGRADED"]),
                "CRITICAL": len([h for h in self.health_history if h["status"] == "CRITICAL"]),
            },
            "recent_checks": self.health_history[-5:],  # Last 5 checks
            "errors": self.error_history[-10:],  # Last 10 errors
        }


def main():
    """Entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor News AI backend health and log errors"
    )
    parser.add_argument(
        "--backend-url",
        default=BACKEND_URL,
        help=f"Backend URL (default: {BACKEND_URL})"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        help="Number of checks before exiting (default: infinite)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=MONITOR_INTERVAL,
        help=f"Check interval in seconds (default: {MONITOR_INTERVAL})"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate report and exit"
    )

    args = parser.parse_args()

    monitor = NewsAIMonitor(
        backend_url=args.backend_url,
        monitor_interval=args.interval
    )

    if args.report:
        # Single check with report generation
        monitor.run_health_check()
        report = monitor.generate_report()
        print(json.dumps(report, indent=2))
    else:
        # Continuous monitoring
        monitor.monitor_loop(max_iterations=args.iterations)


if __name__ == "__main__":
    main()
