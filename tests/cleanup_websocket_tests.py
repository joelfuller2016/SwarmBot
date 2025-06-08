"""
WebSocket Test Cleanup Script
Removes old test files and temporary verification scripts
"""

import os
from pathlib import Path

def cleanup_websocket_tests():
    """Remove old WebSocket test files and verification scripts"""
    
    test_dir = Path(__file__).parent
    
    # Files to remove
    files_to_remove = [
        'test_websocket_events_old.py',
        'test_websocket_resilience_old.py',
        'test_websocket_integration_old.py',
        'test_websocket_performance_old.py',
        'run_websocket_test.py',
        'verify_websocket_fixes.py',
        'verify_all_websocket_tests.py'
    ]
    
    print("WebSocket Test Cleanup")
    print("=" * 50)
    print("\nRemoving old test files and verification scripts...\n")
    
    removed_count = 0
    
    for filename in files_to_remove:
        file_path = test_dir / filename
        if file_path.exists():
            try:
                os.remove(file_path)
                print(f"✓ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"✗ Error removing {filename}: {e}")
        else:
            print(f"- Skipped: {filename} (not found)")
    
    print(f"\nCleanup complete. Removed {removed_count} files.")
    
    # List remaining WebSocket test files
    print("\nRemaining WebSocket test files:")
    print("-" * 30)
    
    remaining_files = [
        'test_websocket_events.py',
        'test_websocket_resilience.py',
        'test_websocket_integration.py',
        'test_websocket_performance.py',
        'test_websocket_suite.py',
        'WEBSOCKET_TEST_GUIDE.md'
    ]
    
    for filename in remaining_files:
        file_path = test_dir / filename
        if file_path.exists():
            print(f"✓ {filename}")
    
    print("\nNote: Run this script only after verifying the new tests work correctly.")

if __name__ == "__main__":
    response = input("Are you sure you want to remove old WebSocket test files? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_websocket_tests()
    else:
        print("Cleanup cancelled.")
