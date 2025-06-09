#!/usr/bin/env python3
"""
SwarmBot Test Cleanup Execution Script
Generated: 2025-06-09T16:25:42.191660
"""
import os
import shutil
from pathlib import Path

# Files to delete
TO_DELETE = [
    "archive\\test_websocket_events_old.py",
    "archive\\test_websocket_integration_old.py",
    "archive\\test_websocket_performance_old.py",
    "archive\\test_websocket_resilience_old.py"
]

# Directories to rename
TO_RENAME = {
    "tests/mcp": "tests/mcp_tests"  # Avoid import conflicts
}

def main():
    tests_dir = Path(__file__).parent / "tests"
    
    print("SwarmBot Test Cleanup Execution")
    print("=" * 60)
    
    # Delete files
    deleted = 0
    for file in TO_DELETE:
        file_path = tests_dir / file
        if file_path.exists():
            print(f"Deleting: {file}")
            file_path.unlink()
            deleted += 1
            
    # Rename directories
    for old_name, new_name in TO_RENAME.items():
        old_path = Path(__file__).parent / old_name
        new_path = Path(__file__).parent / new_name
        if old_path.exists() and not new_path.exists():
            print(f"Renaming: {old_name} -> {new_name}")
            old_path.rename(new_path)
            
    print(f"\nDeleted {deleted} files")
    print("Cleanup complete!")
    
if __name__ == "__main__":
    main()
