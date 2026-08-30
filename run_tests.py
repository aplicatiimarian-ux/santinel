#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test runner for SANTINEL framework test suite.
Runs all tests with coverage reporting and generates summary.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py unit         # Run only unit tests
    python run_tests.py integration  # Run only integration tests
"""

import subprocess
import sys
from pathlib import Path


def run_tests(test_type="all"):
    """Run pytest with appropriate markers and coverage."""
    repo_root = Path(__file__).parent
    tests_dir = repo_root / "tests"

    if not tests_dir.exists():
        print(f"Error: tests directory not found at {tests_dir}")
        return 1

    # Build pytest command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(tests_dir),
        "-v",
        "--tb=short",
        "--cov=core",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_html",
    ]

    # Add marker filter if specified
    if test_type == "unit":
        cmd.append("-m")
        cmd.append("unit")
    elif test_type == "integration":
        cmd.append("-m")
        cmd.append("integration")
    elif test_type == "bilingual":
        cmd.append("-m")
        cmd.append("bilingual")
    elif test_type == "edge_case":
        cmd.append("-m")
        cmd.append("edge_case")
    elif test_type != "all":
        print(f"Unknown test type: {test_type}")
        print("Options: all, unit, integration, bilingual, edge_case")
        return 1

    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 80)

    result = subprocess.run(cmd, cwd=repo_root)

    print("\n" + "=" * 80)
    if result.returncode == 0:
        print("✅ All tests passed!")
        print("\nCoverage report generated in: coverage_html/index.html")
    else:
        print("❌ Some tests failed. See output above for details.")

    return result.returncode


def main():
    """Main entry point."""
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    return run_tests(test_type)


if __name__ == "__main__":
    sys.exit(main())
