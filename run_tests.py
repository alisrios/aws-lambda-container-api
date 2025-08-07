#!/usr/bin/env python3
"""
Test runner script for AWS Lambda Container API
Runs all tests with coverage reporting and quality validation
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with return code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True

def main():
    """Main test runner function"""
    print("🚀 Starting AWS Lambda Container API Test Suite")
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Ensure src directory is in Python path
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    success = True
    
    # Run unit tests
    if not run_command(
        "python -m pytest tests/unit/ -v --tb=short",
        "Unit Tests"
    ):
        success = False
    
    # Run integration tests
    if not run_command(
        "python -m pytest tests/integration/ -v --tb=short",
        "Integration Tests"
    ):
        success = False
    
    # Run all tests with coverage
    if not run_command(
        "python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=85",
        "Full Test Suite with Coverage"
    ):
        success = False
    
    # Generate coverage report
    if not run_command(
        "python -m coverage report --show-missing",
        "Coverage Report"
    ):
        success = False
    
    # Code quality checks (if flake8 is available)
    try:
        subprocess.run(["python", "-m", "flake8", "--version"], 
                      capture_output=True, check=True)
        if not run_command(
            "python -m flake8 src/ tests/ --max-line-length=100 --ignore=E501,W503",
            "Code Quality Check (flake8)"
        ):
            print("⚠️  Code quality issues found, but continuing...")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ️  flake8 not available, skipping code quality checks")
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests completed successfully!")
        print("📊 Coverage report generated in htmlcov/index.html")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())