#!/usr/bin/env python3
"""
Run all SwarmBot tests
"""

import subprocess
import sys
import time
from pathlib import Path


def run_test(script_name, description):
    """Run a test script and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print('='*60)
    
    # Get the tests directory path
    tests_dir = Path(__file__).parent
    script_path = tests_dir / script_name
    
    # Handle special case for demo script
    if script_name == "demo_auto_tools.py":
        script_path = tests_dir.parent / "scripts" / "demos" / script_name
    
    if not script_path.exists():
        print(f"\n[ERROR] Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True,
            cwd=str(tests_dir.parent)  # Run from project root
        )
        
        if result.returncode == 0:
            print(f"\n[OK] {description} - PASSED")
        else:
            print(f"\n[ERROR] {description} - FAILED (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n[ERROR] {description} - ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("[SwarmBot] Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("test_minimal.py", "Minimal functionality test"),
        ("test_config.py", "Configuration test"),
        ("test_enhanced.py", "Enhanced mode test"),
        ("test_fixes.py", "Core fixes test"),
        ("demo_auto_tools.py", "Automatic tools demo")
    ]
    
    passed = 0
    failed = 0
    
    for script, description in tests:
        if run_test(script, description):
            passed += 1
        else:
            failed += 1
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("[Test Summary]")
    print("=" * 60)
    print(f"Total tests: {len(tests)}")
    print(f"[OK] Passed: {passed}")
    print(f"[ERROR] Failed: {failed}")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed! SwarmBot is ready to use.")
        print("\nRun SwarmBot with:")
        print("  python swarmbot.py           # Enhanced mode (default)")
        print("  python swarmbot.py standard  # Standard mode")
    else:
        print("\n[WARNING] Some tests failed. Please check the output above.")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())