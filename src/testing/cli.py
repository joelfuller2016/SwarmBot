#!/usr/bin/env python3
"""
Command-line interface for the SwarmBot Test Executor

Usage:
    python -m src.testing.cli [options] [test_files...]
    
Examples:
    # Execute a single test file
    python -m src.testing.cli tests/test_config.py
    
    # Execute all tests in a directory
    python -m src.testing.cli --directory tests/
    
    # Execute with custom timeout
    python -m src.testing.cli --timeout 60 tests/test_slow.py
    
    # Save results to JSON file
    python -m src.testing.cli --output results.json tests/
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.testing import TestExecutor, TestResult, TestStatus


def print_progress(current: int, total: int, result: TestResult):
    """Print progress information during test execution."""
    status_symbol = {
        TestStatus.PASSED: "✓",
        TestStatus.FAILED: "✗",
        TestStatus.ERROR: "E",
        TestStatus.TIMEOUT: "T",
        TestStatus.SKIPPED: "S",
        TestStatus.NOT_FOUND: "?"
    }
    
    symbol = status_symbol.get(result.status, "?")
    print(f"[{current}/{total}] {symbol} {result.file_path} ({result.execution_time:.2f}s)")


def print_summary(results: List[TestResult]):
    """Print a summary of test results."""
    summary = TestExecutor.generate_summary(results)
    
    print("\n" + "=" * 60)
    print("TEST EXECUTION SUMMARY")
    print("=" * 60)
    
    print(f"\nFiles:")
    print(f"  Total:     {summary['total_files']}")
    print(f"  Passed:    {summary['passed_files']}")
    print(f"  Failed:    {summary['failed_files']}")
    print(f"  Errors:    {summary['error_files']}")
    print(f"  Timeouts:  {summary['timeout_files']}")
    print(f"  Skipped:   {summary['skipped_files']}")
    print(f"  Not Found: {summary['not_found_files']}")
    
    print(f"\nTests:")
    print(f"  Total:     {summary['total_tests']}")
    print(f"  Passed:    {summary['passed_tests']}")
    print(f"  Failed:    {summary['failed_tests']}")
    print(f"  Skipped:   {summary['skipped_tests']}")
    
    print(f"\nExecution Time: {summary['total_execution_time']:.2f} seconds")
    
    if summary['frameworks']:
        print(f"\nFrameworks:")
        for framework, count in summary['frameworks'].items():
            print(f"  {framework}: {count} files")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="SwarmBot Test Executor - Execute and analyze test files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'test_files',
        nargs='*',
        help='Test files to execute'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='Execute all test files in a directory'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        default='test_*.py',
        help='File pattern for directory search (default: test_*.py)'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search directories recursively'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=300,
        help='Timeout per test file in seconds (default: 300)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Save results to JSON file'
    )
    
    parser.add_argument(
        '--project-root',
        help='Project root directory (default: current directory)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output for failed tests'
    )
    
    args = parser.parse_args()
    
    # Initialize executor
    executor = TestExecutor(
        project_root=args.project_root,
        timeout=args.timeout
    )
    
    # Determine which tests to run
    if args.directory:
        print(f"Executing tests in directory: {args.directory}")
        print(f"Pattern: {args.pattern}")
        print(f"Recursive: {not args.no_recursive}")
        print("=" * 60)
        
        results = executor.execute_directory(
            args.directory,
            pattern=args.pattern,
            recursive=not args.no_recursive,
            progress_callback=None if args.quiet else print_progress
        )
    elif args.test_files:
        print(f"Executing {len(args.test_files)} test file(s)")
        print("=" * 60)
        
        results = executor.execute_tests(
            args.test_files,
            progress_callback=None if args.quiet else print_progress
        )
    else:
        parser.error("No test files specified. Use test file paths or --directory option.")
    
    # Print summary
    if not args.quiet:
        print_summary(results)
    
    # Show verbose output for failed tests
    if args.verbose:
        failed_results = [r for r in results if r.status in [TestStatus.FAILED, TestStatus.ERROR]]
        if failed_results:
            print("\n" + "=" * 60)
            print("FAILED TEST DETAILS")
            print("=" * 60)
            
            for result in failed_results:
                print(f"\n{result.file_path}")
                print("-" * len(result.file_path))
                if result.error_message:
                    print(f"Error: {result.error_message}")
                if result.stderr:
                    print("\nStderr:")
                    print(result.stderr[:1000])  # Limit output
                    if len(result.stderr) > 1000:
                        print("... (truncated)")
    
    # Save results to JSON if requested
    if args.output:
        output_data = {
            'execution_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': TestExecutor.generate_summary(results),
            'results': [r.to_dict() for r in results]
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit with appropriate code
    failed_count = sum(1 for r in results if r.status in [TestStatus.FAILED, TestStatus.ERROR, TestStatus.TIMEOUT])
    sys.exit(1 if failed_count > 0 else 0)


if __name__ == '__main__':
    main()
