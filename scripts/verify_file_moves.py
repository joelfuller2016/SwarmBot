"""
Quick verification that moved test files have correct paths
"""
import os
import sys
from pathlib import Path

print("Verifying moved test files...")
print("-" * 60)

# Test files that were moved
test_files = [
    "test_asyncio_fix.py",
    "test_circular_import_fix.py", 
    "test_config_key_fix.py",
    "test_token_fix.py",
    "test_tool_object_fix.py",
    "verify_token_fix.py"
]

# Get the project root (script is in scripts/ directory)
project_root = Path(__file__).parent.parent
tests_dir = project_root / "tests"
errors = []

for test_file in test_files:
    file_path = tests_dir / test_file
    print(f"\nChecking {test_file}...")
    
    if not file_path.exists():
        errors.append(f"  [ERROR] File not found: {file_path}")
        continue
    
    # Read the file and check for path references
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it has proper parent.parent reference
    if "Path(__file__).parent.parent" in content:
        print(f"  [OK] Has correct path reference (parent.parent)")
    elif "Path(__file__).parent" in content and "parent.parent" not in content:
        errors.append(f"  [ERROR] {test_file} has incorrect path reference (only .parent)")
    else:
        print(f"  [WARNING] No path reference found (might be okay)")
    
    # Check if it can import from src
    if "from src" in content or "import src" in content:
        print(f"  [OK] Imports from src directory")

print("\n" + "=" * 60)
if errors:
    print("[ERRORS] Found issues:")
    for error in errors:
        print(error)
else:
    print("[SUCCESS] All moved test files have correct path references!")
print("=" * 60)
