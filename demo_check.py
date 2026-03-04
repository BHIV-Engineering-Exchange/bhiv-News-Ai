#!/usr/bin/env python3
"""
Demo Safety Checker - Pre-Demo Validation
==========================================
Tests News AI system for demo readiness before presentation.

Returns:
  SAFE   - System ready for demo
  UNSAFE - Demo should not proceed; see diagnostics

Usage:
  python demo_check.py
  python demo_check.py --backend http://localhost:8000
  python demo_check.py --frontend http://localhost:3000 --backend http://localhost:8000

Exit code:
  0 = SAFE
  1 = UNSAFE
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple
import time

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
TIMEOUT = 10

# Demo-critical checks
CRITICAL_CHECKS = [
    {
        "name": "Backend Reachability",
        "test": "backend_reachable",
        "required": True,
        "description": "Backend API must be accessible"
    },
    {
        "name": "Backend Health",
        "test": "backend_health",
        "required": True,
        "description": "Backend health check must pass"
    },
    {
        "name": "Pipeline Endpoint",
        "test": "pipeline_endpoint",
        "required": True,
        "description": "Main workflow endpoint must respond"
    },
    {
        "name": "Processing Endpoint",
        "test": "processing_endpoint",
        "required": True,
        "description": "Scraping/summarization must be accessible"
    },
    {
        "name": "Frontend Reachability",
        "test": "frontend_reachable",
        "required": False,
        "description": "Frontend UI should be accessible"
    },
]


class DemoChecker:
    """Pre-demo safety validation."""

    def __init__(self, backend_url=BACKEND_URL, frontend_url=FRONTEND_URL):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.checks: List[Dict] = []
        self.timestamp = datetime.now()
        self.safe = True

    def backend_reachable(self) -> Tuple[bool, str, Dict]:
        """Can we reach the backend?"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=TIMEOUT)
            if response.status_code == 200:
                return True, "Backend responsive", {"url": self.backend_url, "status_code": 200}
            else:
                return False, f"Backend returned status {response.status_code}", {"status_code": response.status_code}
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect. Is backend running?", {"error": "Connection refused"}
        except requests.exceptions.Timeout:
            return False, "Backend response timeout (>10s)", {"error": "Timeout"}
        except Exception as e:
            return False, f"Error: {str(e)}", {"error": str(e)}

    def backend_health(self) -> Tuple[bool, str, Dict]:
        """Check /health endpoint."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=TIMEOUT)
            
            if response.status_code != 200:
                return False, f"Health check returned {response.status_code}", {"status_code": response.status_code}
            
            data = response.json()
            if data.get("status") != "healthy":
                return False, f"Backend status is not healthy: {data.get('status')}", data
            
            # Check key services
            services = data.get("services", {})
            if not services.get("scraping"):
                return False, "Scraping service not available", services
            
            return True, "Backend is healthy", data

        except Exception as e:
            return False, f"Health check failed: {str(e)}", {"error": str(e)}

    def pipeline_endpoint(self) -> Tuple[bool, str, Dict]:
        """Can we call the main pipeline endpoint?"""
        try:
            # Test with actual pipeline call
            payload = {
                "url": "https://example.com",
            }
            
            response = requests.post(
                f"{self.backend_url}/api/unified-news-workflow",
                json=payload,
                timeout=TIMEOUT
            )
            
            # We don't care if it processes successfully, just that it responds
            if response.status_code in [200, 400, 422]:
                return True, "Pipeline endpoint accessible", {"status_code": response.status_code}
            else:
                return False, f"Pipeline returned {response.status_code}", {"status_code": response.status_code}

        except requests.exceptions.Timeout:
            return False, "Pipeline endpoint timeout", {"error": "Timeout"}
        except requests.exceptions.ConnectionError:
            return False, "Cannot reach pipeline endpoint", {"error": "Connection refused"}
        except Exception as e:
            return False, f"Pipeline check failed: {str(e)}", {"error": str(e)}

    def processing_endpoint(self) -> Tuple[bool, str, Dict]:
        """Are processing services (scraping, summarizing) reachable?"""
        endpoints = [
            ("/api/scrape", {"url": "https://example.com"}),
            ("/api/summarize", {"text": "Sample article content."}),
        ]
        
        all_accessible = True
        results = {}
        
        for endpoint, payload in endpoints:
            try:
                response = requests.post(
                    f"{self.backend_url}{endpoint}",
                    json=payload,
                    timeout=TIMEOUT
                )
                
                # Only truly bad if 500+ or connection error
                results[endpoint] = response.status_code
                
                if response.status_code >= 500:
                    all_accessible = False

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                all_accessible = False
                results[endpoint] = "UNREACHABLE"
            except Exception as e:
                results[endpoint] = f"ERROR: {str(e)}"

        if all_accessible:
            return True, "Processing services accessible", results
        else:
            return False, "Some processing services unreachable", results

    def frontend_reachable(self) -> Tuple[bool, str, Dict]:
        """Can we reach the frontend?"""
        try:
            response = requests.get(self.frontend_url, timeout=TIMEOUT)
            
            if response.status_code == 200:
                return True, "Frontend responsive", {"url": self.frontend_url, "status_code": 200}
            else:
                return False, f"Frontend returned {response.status_code}", {"status_code": response.status_code}

        except requests.exceptions.ConnectionError:
            return False, "Cannot connect. Is frontend running?", {"error": "Connection refused"}
        except requests.exceptions.Timeout:
            return False, "Frontend response timeout", {"error": "Timeout"}
        except Exception as e:
            return False, f"Error: {str(e)}", {"error": str(e)}

    def run_check(self, check_name: str, test_func_name: str) -> Dict:
        """Run a single check."""
        test_func = getattr(self, test_func_name, None)
        
        if not test_func:
            return {
                "name": check_name,
                "passed": False,
                "message": f"Test function {test_func_name} not found",
                "details": {},
            }
        
        try:
            start = time.time()
            passed, message, details = test_func()
            elapsed = (time.time() - start) * 1000
            
            return {
                "name": check_name,
                "passed": passed,
                "message": message,
                "details": details,
                "elapsed_ms": round(elapsed, 2),
            }

        except Exception as e:
            return {
                "name": check_name,
                "passed": False,
                "message": f"Exception: {str(e)}",
                "details": {"error": str(e)},
            }

    def run_all_checks(self) -> Dict:
        """Run all demo checks."""
        print("\n" + "=" * 70)
        print("  > NEWS AI - DEMO SAFETY CHECKER")
        print(f"  Backend: {self.backend_url}")
        print(f"  Frontend: {self.frontend_url}")
        print(f"  Started: {self.timestamp.isoformat()}")
        print("=" * 70 + "\n")

        results = {
            "timestamp": self.timestamp.isoformat(),
            "backend_url": self.backend_url,
            "frontend_url": self.frontend_url,
            "checks": [],
            "status": "SAFE",
            "summary": "",
        }

        passed_count = 0
        failed_required = 0

        for check in CRITICAL_CHECKS:
            print(f"[{check['name']}] {check['description']}...")
            
            result = self.run_check(check["name"], check["test"])
            results["checks"].append(result)

            if result["passed"]:
                print(f"  [OK] PASS: {result['message']}")
                passed_count += 1
            else:
                if check["required"]:
                    print(f"  [FAIL] FAIL (CRITICAL): {result['message']}")
                    failed_required += 1
                    self.safe = False
                else:
                    print(f"  [WARN] FAIL (WARNING): {result['message']}")

            print()

        # Determine overall status
        if self.safe:
            results["status"] = "SAFE"
            status_icon = "[OK]"
        else:
            results["status"] = "UNSAFE"
            status_icon = "[FAIL]"

        results["summary"] = f"{status_icon} Demo Status: {results['status']} | Passed: {passed_count}/{len(CRITICAL_CHECKS)} | Failed Critical: {failed_required}"

        # Print summary
        print("=" * 70)
        print(f"  {results['summary']}")
        print("=" * 70)

        if not self.safe:
            print("\n[WARN] DEMO SAFETY CHECK FAILED")
            print("\nFailing Checks:")
            for check in results["checks"]:
                if not check["passed"] and any(c["required"] and c["name"] == check["name"] for c in CRITICAL_CHECKS):
                    print(f"  * {check['name']}: {check['message']}")
            print("\nAction Required: See DEMO_RECOVERY.md for troubleshooting steps.")
        else:
            print("\n[OK] DEMO IS READY TO PROCEED")

        return results

    def save_report(self, filename: str = "demo_check_report.json"):
        """Save check results to file."""
        # We'll do this after running checks
        pass


def main():
    """Entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Check News AI system for demo readiness")
    parser.add_argument(
        "--backend",
        default=BACKEND_URL,
        help=f"Backend URL (default: {BACKEND_URL})"
    )
    parser.add_argument(
        "--frontend",
        default=FRONTEND_URL,
        help=f"Frontend URL (default: {FRONTEND_URL})"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    checker = DemoChecker(backend_url=args.backend, frontend_url=args.frontend)
    results = checker.run_all_checks()

    if args.json:
        print(json.dumps(results, indent=2))

    # Exit with appropriate code
    sys.exit(0 if checker.safe else 1)


if __name__ == "__main__":
    main()
