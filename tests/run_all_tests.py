#!/usr/bin/env python3
"""
Run all SwarmBot tests
"""

import subprocess
import sys
import time


def run_test(script_name, description):
    """Run a test script and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✅ {description} - PASSED")
        else:
            print(f"\n❌ {description} - FAILED (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n❌ {description} - ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 SwarmBot Comprehensive Test Suite")
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
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! SwarmBot is ready to use.")
        print("\nRun SwarmBot with:")
        print("  python run_swarmbot.py           # Standard mode")
        print("  python run_swarmbot.py enhanced  # Enhanced mode")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())