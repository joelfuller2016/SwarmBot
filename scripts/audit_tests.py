#!/usr/bin/env python3
"""
SwarmBot Test Audit Runner

This script uses the Test Executor to audit all tests in the SwarmBot project
and generate a comprehensive report.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.testing import TestExecutor, TestStatus


def audit_swarmbot_tests():
    """Run a complete audit of SwarmBot tests."""
    print("SwarmBot Test Suite Audit")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Initialize executor
    project_root = Path(__file__).parent.parent
    executor = TestExecutor(project_root=project_root)
    
    # Define test categories
    categories = {
        "Unit Tests": {
            "path": "tests/unit",
            "pattern": "test_*.py",
            "recursive": True
        },
        "Integration Tests": {
            "path": "tests/integration", 
            "pattern": "test_*.py",
            "recursive": True
        },
        "MCP Tests": {
            "path": "tests/mcp_tests",
            "pattern": "test_*.py", 
            "recursive": True
        },
        "Fix Verification Tests": {
            "path": "tests",
            "pattern": "test_*_fix.py",
            "recursive": False
        },
        "WebSocket Tests": {
            "path": "tests",
            "pattern": "test_websocket_*.py",
            "recursive": False
        },
        "AsyncIO Tests": {
            "path": "tests",
            "pattern": "test_asyncio_*.py",
            "recursive": False
        },
        "Dashboard Tests": {
            "path": "tests",
            "pattern": "test_dashboard_*.py",
            "recursive": False
        },
        "Other Tests": {
            "path": "tests",
            "pattern": "test_*.py",
            "recursive": False
        }
    }
    
    # Track all results
    all_results = []
    category_summaries = {}
    
    # Process each category
    for category_name, config in categories.items():
        print(f"\n{category_name}")
        print("-" * len(category_name))
        
        path = project_root / config["path"]
        if not path.exists():
            print(f"  Path not found: {path}")
            continue
            
        # Execute tests in this category
        try:
            results = executor.execute_directory(
                path,
                pattern=config["pattern"],
                recursive=config["recursive"],
                progress_callback=lambda c, t, r: print(f"  [{c}/{t}] {Path(r.file_path).name}: {r.status.value}")
            )
            
            # Filter out tests from other categories for "Other Tests"
            if category_name == "Other Tests":
                # Exclude tests that belong to other categories
                exclude_patterns = [
                    "test_*_fix.py",
                    "test_websocket_*.py", 
                    "test_asyncio_*.py",
                    "test_dashboard_*.py"
                ]
                results = [r for r in results if not any(
                    Path(r.file_path).match(pattern) for pattern in exclude_patterns
                )]
            
            all_results.extend(results)
            category_summaries[category_name] = TestExecutor.generate_summary(results)
            
        except Exception as e:
            print(f"  Error processing category: {e}")
    
    # Generate overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    overall_summary = TestExecutor.generate_summary(all_results)
    
    print(f"\nTotal Files Tested: {overall_summary['total_files']}")
    print(f"  Passed:     {overall_summary['passed_files']} ({overall_summary['passed_files']/overall_summary['total_files']*100:.1f}%)")
    print(f"  Failed:     {overall_summary['failed_files']}")
    print(f"  Errors:     {overall_summary['error_files']}")
    print(f"  Timeouts:   {overall_summary['timeout_files']}")
    print(f"  Skipped:    {overall_summary['skipped_files']}")
    print(f"  Not Found:  {overall_summary['not_found_files']}")
    
    print(f"\nTotal Tests Run: {overall_summary['total_tests']}")
    print(f"  Passed:     {overall_summary['passed_tests']}")
    print(f"  Failed:     {overall_summary['failed_tests']}")
    print(f"  Skipped:    {overall_summary['skipped_tests']}")
    
    print(f"\nTotal Execution Time: {overall_summary['total_execution_time']:.2f} seconds")
    
    # Category breakdown
    print("\n" + "=" * 80)
    print("CATEGORY BREAKDOWN")
    print("=" * 80)
    
    for category, summary in category_summaries.items():
        if summary['total_files'] > 0:
            print(f"\n{category}:")
            print(f"  Files: {summary['total_files']} (Passed: {summary['passed_files']}, Failed: {summary['failed_files']})")
            print(f"  Tests: {summary['total_tests']} (Passed: {summary['passed_tests']}, Failed: {summary['failed_tests']})")
    
    # List failed tests
    failed_results = [r for r in all_results if r.status in [TestStatus.FAILED, TestStatus.ERROR, TestStatus.TIMEOUT]]
    
    if failed_results:
        print("\n" + "=" * 80)
        print("FAILED TESTS")
        print("=" * 80)
        
        for result in failed_results:
            print(f"\n{result.file_path}")
            print(f"  Status: {result.status.value}")
            if result.error_message:
                print(f"  Error: {result.error_message}")
            if result.exit_code is not None:
                print(f"  Exit Code: {result.exit_code}")
    
    # Generate detailed report
    report_dir = project_root / "test_audit_reports"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"test_audit_{timestamp}.json"
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "overall_summary": overall_summary,
        "category_summaries": category_summaries,
        "failed_tests": [r.to_dict() for r in failed_results],
        "all_results": [r.to_dict() for r in all_results]
    }
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n\nDetailed report saved to: {report_file}")
    
    # Generate recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if overall_summary['failed_files'] > 0:
        print("\n1. Fix failing tests:")
        for result in failed_results[:5]:  # Show first 5
            print(f"   - {Path(result.file_path).name}")
        if len(failed_results) > 5:
            print(f"   ... and {len(failed_results) - 5} more")
    
    if overall_summary['error_files'] > 0:
        print("\n2. Investigate test errors (import issues, syntax errors)")
    
    if overall_summary['timeout_files'] > 0:
        print("\n3. Review tests that timed out - they may have infinite loops or be too slow")
    
    if overall_summary['not_found_files'] > 0:
        print("\n4. Check for missing test files referenced in test runners")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return overall_summary['failed_files'] == 0


if __name__ == "__main__":
    success = audit_swarmbot_tests()
    sys.exit(0 if success else 1)
