#!/usr/bin/env python3
"""
RL Test Dataset Generator and Runner
Generates 10 test cases and evaluates RL improvements
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rl.feedback_service import rl_feedback_service

async def main():
    """Generate test dataset and run RL evaluation"""
    print("🧠 News AI RL Test Suite")
    print("=" * 50)

    # Generate test dataset
    print("📊 Generating 10 test cases...")
    test_cases = await rl_feedback_service.generate_test_dataset(10)

    # Save test cases to file
    test_file = Path("logs/rl/rl_test_cases.json")
    test_file.parent.mkdir(parents=True, exist_ok=True)

    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "test_cases": test_cases
        }, f, indent=2, ensure_ascii=False)

    print(f"✅ Test cases saved to {test_file}")

    # Run RL evaluation on test cases
    print("\n🔬 Running RL evaluation on test dataset...")
    results = await rl_feedback_service.run_rl_test_suite(test_cases)

    # Save results
    results_file = Path("logs/rl/rl_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Test results saved to {results_file}")

    # Print summary
    print("\n📈 Test Results Summary:")
    print("-" * 30)
    summary = results["test_summary"]
    print(f"Total Cases: {summary['total_cases']}")
    print(f"Successful Evaluations: {summary['successful_evaluations']}")
    print(f"Average Reward Score: {summary['avg_reward']:.3f}")
    print(f"Average Latency: {summary['avg_latency']:.3f}s")
    print(f"Correction Rate: {summary['correction_rate']:.3f}")

    print("\n🎯 Category Performance:")
    for category, perf in results["category_performance"].items():
        print(f"  {category}: {perf['avg_reward']:.3f} (n={perf['count']})")

    # Check if metrics file exists and show recent entries
    metrics_file = Path("logs/rl/rl_metrics.jsonl")
    if metrics_file.exists():
        print(f"\n📝 RL Metrics logged to {metrics_file}")
        with open(metrics_file, 'r') as f:
            lines = f.readlines()
            print(f"Total logged events: {len(lines)}")

    print("\n🎉 RL Test Suite Complete!")

if __name__ == "__main__":
    asyncio.run(main())