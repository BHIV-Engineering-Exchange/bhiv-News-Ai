#!/usr/bin/env python3
"""
Test runner script for News AI Backend
Run comprehensive tests for the API endpoints
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running News AI Backend Tests...")
    print("=" * 50)
    
    # Install test dependencies if needed
    print("📦 Installing test dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to install test dependencies: {result.stderr}")
        return False
    
    # Run tests
    print("🚀 Running pytest...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ Tests failed with return code: {result.returncode}")
        return False

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"🎯 Running specific test: {test_name}")
    result = subprocess.run([
        sys.executable, "-m", "pytest", f"tests/{test_name}", "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)