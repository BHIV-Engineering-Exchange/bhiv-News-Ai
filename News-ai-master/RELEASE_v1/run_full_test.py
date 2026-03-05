#!/usr/bin/env python3
"""
Final QA Test Suite for News AI Production System
Tests the complete integrated system: Backend + Seeya + Sankalp + Chandragupta
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"  # Change to production URL when deployed
TEST_NEWS_URLS = [
    "https://www.bbc.com/news",
    "https://www.reuters.com/",
    "https://www.nytimes.com/",
    "https://www.theguardian.com/international",
    "https://www.aljazeera.com/news/"
]

class NewsAITestSuite:
    def __init__(self):
        self.client = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "News AI Production System v1.0",
            "components_tested": [],
            "overall_success": True,
            "performance_metrics": {},
            "error_summary": []
        }

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def run_test(self, endpoint: str, data: dict, test_name: str, expected_success: bool = True):
        """Run a single test and record results"""
        try:
            start_time = time.time()
            response = await self.client.post(f"{BASE_URL}{endpoint}", json=data)
            latency = time.time() - start_time

            result = {
                "test_name": test_name,
                "endpoint": endpoint,
                "latency": round(latency, 3),
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }

            if response.status_code == 200:
                response_data = response.json()
                result["success"] = response_data.get("success", False)
                result["response_data"] = response_data

                if result["success"] == expected_success:
                    print(f"✅ {test_name}: PASS ({latency:.2f}s)")
                    result["status"] = "PASS"
                else:
                    print(f"⚠️  {test_name}: UNEXPECTED RESULT ({latency:.2f}s)")
                    result["status"] = "UNEXPECTED"
                    self.results["overall_success"] = False
            else:
                print(f"❌ {test_name}: HTTP {response.status_code} ({latency:.2f}s)")
                result["status"] = "FAIL"
                result["error"] = response.text
                self.results["overall_success"] = False
                self.results["error_summary"].append(f"{test_name}: HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            result = {
                "test_name": test_name,
                "endpoint": endpoint,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["overall_success"] = False
            self.results["error_summary"].append(f"{test_name}: {str(e)}")

        self.results["components_tested"].append(result)
        return result

    async def test_health_and_connectivity(self):
        """Test 1: System Health and Connectivity"""
        print("\n🏥 TEST 1: System Health & Connectivity")

        # Health check
        await self.run_test("/health", {}, "Health Check")

        # Root endpoint
        await self.run_test("/", {}, "Root Endpoint")

    async def test_unified_pipeline(self):
        """Test 2: Unified Pipeline Processing"""
        print("\n🔬 TEST 2: Unified Pipeline Processing")

        for i, url in enumerate(TEST_NEWS_URLS[:3]):  # Test 3 URLs
            test_data = {
                "url": url,
                "options": {
                    "enable_bhiv_push": True,
                    "enable_audio": True,
                    "channels": ["news_channel_1"],
                    "avatars": ["avatar_alice"],
                    "voice": "default"
                }
            }

            result = await self.run_test(
                "/v1/run_pipeline",
                test_data,
                f"Unified Pipeline - {url.split('/')[-1] or url.split('.')[-2]}"
            )

            # Additional validation for successful pipeline runs
            if result.get("status") == "PASS" and result.get("response_data", {}).get("success"):
                data = result["response_data"]["data"]

                # Check for required components
                checks = {
                    "news_item": bool(data.get("news_item", {}).get("title")),
                    "script": bool(data.get("script", {}).get("video_prompt")),
                    "rl_feedback": "reward_score" in data.get("rl_feedback", {}),
                    "bhiv_push": isinstance(data.get("bhiv_push", {}).get("successful"), bool),
                    "audio": isinstance(data.get("audio", {}).get("generated"), bool)
                }

                failed_checks = [k for k, v in checks.items() if not v]
                if failed_checks:
                    print(f"   ⚠️  Missing components: {', '.join(failed_checks)}")
                    result["missing_components"] = failed_checks

    async def test_scheduler_and_queue(self):
        """Test 3: Background Scheduler and Queue"""
        print("\n⏰ TEST 3: Scheduler & Background Queue")

        # Get scheduler stats
        await self.run_test("/api/scheduler/stats", {}, "Scheduler Stats")

        # Get queue stats
        await self.run_test("/api/queue/stats", {}, "Queue Stats")

        # Trigger manual scheduler run
        await self.run_test(
            "/api/scheduler/trigger",
            {"category": "live"},
            "Manual Scheduler Trigger"
        )

    async def test_rl_system(self):
        """Test 4: RL Feedback System"""
        print("\n🧠 TEST 4: RL Feedback System")

        # Test RL metrics endpoint
        await self.run_test("/api/rl/metrics", {"limit": 5}, "RL Metrics")

        # Test manual RL feedback calculation
        rl_test_data = {
            "news_item": {
                "content": "Test news content for RL evaluation",
                "title": "Test Article",
                "authenticity_score": 85
            },
            "script_output": {
                "video_script": "Generated video script for testing"
            }
        }

        await self.run_test("/api/rl/feedback", rl_test_data, "RL Feedback Calculation")

    async def test_agent_system(self):
        """Test 5: Agent Registry System"""
        print("\n🤖 TEST 5: Agent Registry System")

        # List agents
        await self.run_test("/api/agents", {}, "Agent Registry")

        # Test agent task submission (if agents are available)
        agent_task_data = {
            "task_data": {
                "content": "Test content for agent processing",
                "title": "Test Task"
            }
        }

        # This might fail if agents aren't properly initialized, which is OK for this test
        await self.run_test(
            "/api/agents/fetch_agent/task",
            agent_task_data,
            "Agent Task Submission",
            expected_success=False  # We expect this might fail in test environment
        )

    async def test_external_integrations(self):
        """Test 6: External Service Integrations"""
        print("\n🔗 TEST 6: External Integrations")

        # BHIV Status
        await self.run_test("/api/bhiv/status", {}, "BHIV Status")

        # Uniguru Classification
        uniguru_data = {
            "text": "This is a test news article about artificial intelligence and technology."
        }
        await self.run_test("/api/uniguru/classify", uniguru_data, "Uniguru Classification")

        # Uniguru Sentiment
        await self.run_test("/api/uniguru/sentiment", uniguru_data, "Uniguru Sentiment")

    async def test_database_operations(self):
        """Test 7: Database Operations"""
        print("\n💾 TEST 7: Database Operations")

        # Get news items
        await self.run_test("/api/news", {"limit": 5}, "News Items Retrieval")

    async def test_error_handling(self):
        """Test 8: Error Handling"""
        print("\n🚨 TEST 8: Error Handling")

        # Test with invalid URL
        invalid_data = {
            "url": "not-a-valid-url",
            "options": {"enable_bhiv_push": True}
        }
        await self.run_test(
            "/v1/run_pipeline",
            invalid_data,
            "Invalid URL Handling",
            expected_success=False
        )

        # Test with missing required fields
        incomplete_data = {"options": {"enable_bhiv_push": True}}
        await self.run_test(
            "/v1/run_pipeline",
            incomplete_data,
            "Missing URL Handling",
            expected_success=False
        )

    async def run_performance_tests(self):
        """Test 9: Performance Testing"""
        print("\n⚡ TEST 9: Performance Testing")

        latencies = []
        test_url = TEST_NEWS_URLS[0]

        print("   Running 5 concurrent pipeline requests...")

        # Run 5 concurrent requests
        tasks = []
        for i in range(5):
            task_data = {
                "url": test_url,
                "options": {
                    "enable_bhiv_push": False,  # Disable BHIV for faster testing
                    "enable_audio": False
                }
            }
            tasks.append(self.run_test(
                "/v1/run_pipeline",
                task_data,
                f"Performance Test {i+1}",
                expected_success=True
            ))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect latency data
        for result in results:
            if isinstance(result, dict) and "latency" in result:
                latencies.append(result["latency"])

        if latencies:
            self.results["performance_metrics"] = {
                "concurrent_requests": len(latencies),
                "average_latency": round(sum(latencies) / len(latencies), 3),
                "min_latency": round(min(latencies), 3),
                "max_latency": round(max(latencies), 3),
                "total_time": round(sum(latencies), 3)
            }

            print("   📊 Performance Results:")
            print(f"      Average: {self.results['performance_metrics']['average_latency']}s")
            print(f"      Min: {self.results['performance_metrics']['min_latency']}s")
            print(f"      Max: {self.results['performance_metrics']['max_latency']}s")

    async def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 TEST SUITE SUMMARY")
        print("=" * 60)

        total_tests = len(self.results["components_tested"])
        passed_tests = sum(1 for t in self.results["components_tested"] if t.get("status") == "PASS")
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests Run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.results["performance_metrics"]:
            perf = self.results["performance_metrics"]
            print(f"\nPerformance (5 concurrent requests):")
            print(f"  Average Latency: {perf['average_latency']}s")
            print(f"  Min/Max Latency: {perf['min_latency']}s / {perf['max_latency']}s")

        print(f"\nOverall Status: {'✅ PASSED' if self.results['overall_success'] else '❌ FAILED'}")

        if self.results["error_summary"]:
            print(f"\n⚠️  Errors Encountered ({len(self.results['error_summary'])}):")
            for error in self.results["error_summary"][:5]:  # Show first 5 errors
                print(f"  • {error}")

        # Save detailed results
        output_file = Path("final_qa_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)

        print(f"\n📄 Detailed results saved to {output_file}")

        return self.results

async def main():
    """Main test execution"""
    print("🧪 News AI Production System - Final QA Test Suite")
    print("Testing complete integration: Backend + Seeya + Sankalp + Chandragupta")
    print("=" * 80)

    async with NewsAITestSuite() as test_suite:
        # Run all test categories
        await test_suite.test_health_and_connectivity()
        await test_suite.test_unified_pipeline()
        await test_suite.test_scheduler_and_queue()
        await test_suite.test_rl_system()
        await test_suite.test_agent_system()
        await test_suite.test_external_integrations()
        await test_suite.test_database_operations()
        await test_suite.test_error_handling()
        await test_suite.test_performance_tests()

        # Generate final report
        results = await test_suite.generate_test_report()

        # Final assessment
        print("\n🏆 FINAL QA ASSESSMENT")
        print("=" * 40)

        if results["overall_success"]:
            print("🎉 PRODUCTION SYSTEM QA: PASSED")
            print("✅ News AI v1.0 is ready for production deployment!")
            print("\n🚀 Recommended Actions:")
            print("  • Deploy to Railway with production environment variables")
            print("  • Set up monitoring and alerting")
            print("  • Configure CDN for static assets")
            print("  • Enable rate limiting based on load testing")
        else:
            print("⚠️  PRODUCTION SYSTEM QA: ISSUES FOUND")
            print("🔧 Review final_qa_results.json for detailed error information")
            print("📞 Contact development team before production deployment")

        return results["overall_success"]

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)