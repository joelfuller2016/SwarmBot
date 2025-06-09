#!/usr/bin/env python3
"""
Test script to verify the Test Executor functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing import TestExecutor, TestStatus


def test_single_file():
    """Test executing a single test file."""
    print("Testing single file execution...")
    
    executor = TestExecutor()
    
    # Try to execute a known test file
    test_file = Path(__file__).parent / "test_dummy_example.py"
    
    if test_file.exists():
        result = executor.execute_test(test_file)
        
        print(f"File: {result.file_path}")
        print(f"Status: {result.status.value}")
        print(f"Framework: {result.framework}")
        print(f"Execution time: {result.execution_time:.2f}s")
        print(f"Exit code: {result.exit_code}")
        
        if result.test_count is not None:
            print(f"Tests: {result.test_count}")
            print(f"Passed: {result.passed_count}")
            print(f"Failed: {result.failed_count}")
            print(f"Skipped: {result.skipped_count}")
    else:
        print(f"Test file not found: {test_file}")


def test_directory():
    """Test executing all tests in the unit directory."""
    print("\nTesting directory execution...")
    
    executor = TestExecutor()
    
    # Try the unit tests directory
    unit_dir = Path(__file__).parent / "unit"
    
    if unit_dir.exists():
        results = executor.execute_directory(
            unit_dir,
            recursive=False,
            progress_callback=lambda c, t, r: print(f"  [{c}/{t}] {r.file_path}: {r.status.value}")
        )
        
        # Generate summary
        summary = TestExecutor.generate_summary(results)
        
        print("\nSummary:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Passed: {summary['passed_files']}")
        print(f"  Failed: {summary['failed_files']}")
        print(f"  Total execution time: {summary['total_execution_time']:.2f}s")
    else:
        print(f"Unit test directory not found: {unit_dir}")


def test_timeout():
    """Test timeout functionality."""
    print("\nTesting timeout functionality...")
    
    # Create a test file that will timeout
    timeout_test = Path(__file__).parent / "test_timeout_demo.py"
    timeout_test.write_text("""
import time
def test_slow():
    time.sleep(10)  # This will timeout with default 5 second timeout
    assert True
""")
    
    try:
        executor = TestExecutor(timeout=2)  # 2 second timeout
        result = executor.execute_test(timeout_test)
        
        print(f"Status: {result.status.value}")
        print(f"Expected TIMEOUT status: {result.status == TestStatus.TIMEOUT}")
    finally:
        # Clean up
        if timeout_test.exists():
            timeout_test.unlink()


if __name__ == "__main__":
    print("SwarmBot Test Executor Demo")
    print("=" * 60)
    
    test_single_file()
    test_directory()
    test_timeout()
    
    print("\nDemo completed!")
