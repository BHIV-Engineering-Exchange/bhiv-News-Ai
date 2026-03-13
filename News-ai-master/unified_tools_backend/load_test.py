#!/usr/bin/env python3
"""
Production Load Testing Script for News AI Backend
Tests performance under load and captures comprehensive metrics for Integration-B validation
"""

import asyncio
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
import httpx
import numpy as np

class LoadTester:
    """Production load testing for News AI Backend"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def run_load_test(self, concurrent_users: List[int], requests_per_user: int = 10) -> Dict[str, Any]:
        """Run comprehensive load test across multiple concurrency levels"""

        print(f"Starting load test against {self.base_url}")
        print(f"Testing concurrency levels: {concurrent_users}")
        print(f"Requests per user: {requests_per_user}")
        print("=" * 80)

        all_results = []

        for users in concurrent_users:
            print(f"\nTesting with {users} concurrent users...")
            result = await self._test_concurrency_level(users, requests_per_user)
            all_results.append(result)

            # Brief pause between test levels
            await asyncio.sleep(2)

        # Generate comprehensive report
        report = self._generate_report(all_results, concurrent_users, requests_per_user)

        # Save results
        self._save_results(report)

        return report

    async def _test_concurrency_level(self, concurrent_users: int, requests_per_user: int) -> Dict[str, Any]:
        """Test a specific concurrency level"""

        start_time = time.time()

        # Create tasks for concurrent users
        tasks = []
        for user_id in range(concurrent_users):
            task = asyncio.create_task(self._simulate_user(user_id, requests_per_user))
            tasks.append(task)

        # Wait for all users to complete
        user_results = await asyncio.gather(*tasks, return_exceptions=True)

        total_duration = time.time() - start_time

        # Aggregate results
        return self._aggregate_user_results(user_results, concurrent_users, requests_per_user, total_duration)

    async def _simulate_user(self, user_id: int, num_requests: int) -> Dict[str, Any]:
        """Simulate a single user's behavior"""

        user_results = {
            "user_id": user_id,
            "requests": [],
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "errors": []
        }

        # Define request patterns (mix of endpoints)
        endpoints = [
            ("GET", "/health", None),
            ("GET", "/api/agents", None),
            ("POST", "/api/rl/feedback", {
                "news_item": {"title": "Test", "content": "Test content", "authenticity_score": 85},
                "script_output": {"video_script": "Test script"}
            }),
            ("POST", "/api/uniguru/sentiment", {"text": "This is a test news article about technology."}),
            ("GET", "/api/rl/metrics", None),
        ]

        for i in range(num_requests):
            endpoint_idx = i % len(endpoints)
            method, path, data = endpoints[endpoint_idx]

            request_start = time.time()

            try:
                if method == "GET":
                    response = await self.client.get(f"{self.base_url}{path}")
                else:
                    response = await self.client.post(
                        f"{self.base_url}{path}",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    )

                request_duration = time.time() - request_start

                success = response.status_code in [200, 201, 202]

                user_results["requests"].append({
                    "endpoint": path,
                    "method": method,
                    "status_code": response.status_code,
                    "duration": request_duration,
                    "success": success
                })

                if success:
                    user_results["successful_requests"] += 1
                else:
                    user_results["failed_requests"] += 1
                    user_results["errors"].append({
                        "endpoint": path,
                        "status_code": response.status_code,
                        "error": response.text[:200]  # Truncate long errors
                    })

            except Exception as e:
                request_duration = time.time() - request_start
                user_results["requests"].append({
                    "endpoint": path,
                    "method": method,
                    "status_code": None,
                    "duration": request_duration,
                    "success": False,
                    "error": str(e)
                })
                user_results["failed_requests"] += 1
                user_results["errors"].append({
                    "endpoint": path,
                    "error": str(e)
                })

            user_results["total_requests"] += 1

            # Small delay between requests to simulate realistic user behavior
            await asyncio.sleep(0.1)

        return user_results

    def _aggregate_user_results(self, user_results: List[Any], concurrent_users: int,
                              requests_per_user: int, total_duration: float) -> Dict[str, Any]:
        """Aggregate results from all users in a concurrency level"""

        all_requests = []
        endpoint_stats = {}
        error_summary = {}

        total_requests = 0
        successful_requests = 0
        failed_requests = 0

        for user_result in user_results:
            if isinstance(user_result, Exception):
                # Handle exceptions from user tasks
                failed_requests += requests_per_user
                total_requests += requests_per_user
                continue

            total_requests += user_result["total_requests"]
            successful_requests += user_result["successful_requests"]
            failed_requests += user_result["failed_requests"]

            # Collect all request data
            for req in user_result["requests"]:
                all_requests.append(req["duration"])

                # Aggregate by endpoint
                endpoint = req["endpoint"]
                if endpoint not in endpoint_stats:
                    endpoint_stats[endpoint] = {
                        "requests": 0,
                        "successful": 0,
                        "total_latency": 0.0
                    }

                endpoint_stats[endpoint]["requests"] += 1
                endpoint_stats[endpoint]["total_latency"] += req["duration"]
                if req["success"]:
                    endpoint_stats[endpoint]["successful"] += 1

            # Aggregate errors
            for error in user_result["errors"]:
                error_key = error.get("status_code") or error.get("error", "Unknown")
                error_summary[error_key] = error_summary.get(error_key, 0) + 1

        # Calculate latency statistics
        if all_requests:
            latencies = sorted(all_requests)
            latency_stats = {
                "mean": statistics.mean(latencies),
                "median": statistics.median(latencies),
                "min": min(latencies),
                "max": max(latencies),
                "p95": np.percentile(latencies, 95),
                "p99": np.percentile(latencies, 99)
            }
        else:
            latency_stats = {"mean": 0, "median": 0, "min": 0, "max": 0, "p95": 0, "p99": 0}

        # Process endpoint breakdown
        endpoint_breakdown = {}
        for endpoint, stats in endpoint_stats.items():
            endpoint_breakdown[endpoint] = {
                "requests": stats["requests"],
                "success_rate": (stats["successful"] / stats["requests"]) * 100 if stats["requests"] > 0 else 0,
                "avg_latency": stats["total_latency"] / stats["requests"] if stats["requests"] > 0 else 0
            }

        return {
            "concurrent_users": concurrent_users,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests) * 100 if total_requests > 0 else 0,
            "total_duration": total_duration,
            "requests_per_second": total_requests / total_duration if total_duration > 0 else 0,
            "latency_stats": latency_stats,
            "endpoint_breakdown": endpoint_breakdown,
            "error_summary": error_summary
        }

    def _generate_report(self, results: List[Dict], concurrent_users: List[int],
                        requests_per_user: int) -> Dict[str, Any]:
        """Generate comprehensive load test report"""

        # Find best and worst performance
        best_performance = max(results, key=lambda x: x["success_rate"])
        worst_performance = min(results, key=lambda x: x["success_rate"])

        # Generate recommendations
        recommendations = self._generate_recommendations(results)

        report = {
            "test_metadata": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "concurrent_users_tested": concurrent_users,
                "requests_per_user": requests_per_user,
                "test_duration_per_level": "auto",
                "total_test_duration": sum(r["total_duration"] for r in results)
            },
            "load_test_results": results,
            "recommendations": recommendations,
            "summary": {
                "total_load_levels": len(results),
                "max_concurrent_users_tested": max(concurrent_users),
                "best_performance": {
                    "users": best_performance["concurrent_users"],
                    "success_rate": best_performance["success_rate"]
                },
                "worst_performance": {
                    "users": worst_performance["concurrent_users"],
                    "success_rate": worst_performance["success_rate"]
                },
                "recommendations_count": len(recommendations),
                "load_test_conclusion": self._generate_conclusion(results)
            }
        }

        return report

    def _generate_recommendations(self, results: List[Dict]) -> List[Dict]:
        """Generate performance recommendations based on results"""

        recommendations = []

        # Check for performance degradation
        baseline = results[0]  # Single user performance
        for result in results[1:]:
            latency_increase = result["latency_stats"]["mean"] / baseline["latency_stats"]["mean"]

            if latency_increase > 5.0:
                recommendations.append({
                    "type": "scaling",
                    "priority": "high",
                    "message": f"Performance degrades significantly at {result['concurrent_users']} users. Consider horizontal scaling.",
                    "metric": f"Latency increases {latency_increase:.1f}x from baseline"
                })

            if result["success_rate"] < 95.0:
                recommendations.append({
                    "type": "reliability",
                    "priority": "high",
                    "message": f"Success rate drops below 95% at {result['concurrent_users']} users.",
                    "metric": f"{result['success_rate']:.1f}% success rate at {result['concurrent_users']} concurrent users"
                })

            if result["latency_stats"]["p95"] > 5.0:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "message": f"P95 latency exceeds 5s at {result['concurrent_users']} users.",
                    "metric": f"P95 latency: {result['latency_stats']['p95']:.1f}s at {result['concurrent_users']} concurrent users"
                })

        # Check maximum throughput
        max_throughput = max(r["requests_per_second"] for r in results)
        max_throughput_result = max(results, key=lambda x: x["requests_per_second"])

        recommendations.append({
            "type": "capacity",
            "priority": "info",
            "message": f"Maximum throughput achieved: {max_throughput:.1f} requests/second",
            "metric": f"{max_throughput:.1f} requests/second at {max_throughput_result['concurrent_users']} concurrent users"
        })

        return recommendations

    def _generate_conclusion(self, results: List[Dict]) -> str:
        """Generate test conclusion"""

        acceptable_load = None
        for result in results:
            if result["success_rate"] >= 95.0 and result["latency_stats"]["p95"] <= 2.0:
                acceptable_load = result["concurrent_users"]
            else:
                break

        if acceptable_load:
            return f"System shows good performance up to {acceptable_load} concurrent users, with performance degradation starting at higher loads. Production deployment should include monitoring and auto-scaling capabilities."
        else:
            return "System performance needs improvement. Even single-user performance is below acceptable thresholds. Consider optimization before production deployment."

    def _save_results(self, report: Dict[str, Any]):
        """Save test results to file"""

        filename = f"load_test_results_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nDetailed results saved to {filename}")


async def main():
    """Main load testing function"""

    # Configuration
    BASE_URL = "http://localhost:8000"  # Change this to your running server
    CONCURRENT_USERS = [1, 5, 10]  # Reduced for safety, add 20 if system can handle
    REQUESTS_PER_USER = 10

    print("News AI Backend Load Testing")
    print("=" * 60)
    print(f"Target URL: {BASE_URL}")
    print(f"Concurrency levels: {CONCURRENT_USERS}")
    print(f"Requests per user: {REQUESTS_PER_USER}")
    print("\n⚠️  WARNING: This will send real HTTP requests to your server!")
    print("   Make sure the backend is running and can handle the load.")
    print("   Consider running this in a staging environment first.")
    print()

    try:
        async with LoadTester(BASE_URL) as tester:
            report = await tester.run_load_test(CONCURRENT_USERS, REQUESTS_PER_USER)

        # Print summary
        print("\nLOAD TEST SUMMARY")
        print("=" * 60)
        print(f"Load levels tested: {report['summary']['total_load_levels']}")
        print(f"Max concurrent users: {report['summary']['max_concurrent_users_tested']}")
        print(f"Recommendations: {report['summary']['recommendations_count']}")

        print("\nPerformance by Load Level:")
        for result in report["load_test_results"]:
            users = result["concurrent_users"]
            success = result["success_rate"]
            throughput = result["requests_per_second"]
            p95_latency = result["latency_stats"]["p95"]
            print(".1f")

        if report["recommendations"]:
            print("\nKey Recommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec['message']}")

        print(f"\nConclusion: {report['summary']['load_test_conclusion']}")

    except Exception as e:
        print(f"❌ Load test failed: {e}")
        print("Make sure the backend server is running on the specified URL")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)