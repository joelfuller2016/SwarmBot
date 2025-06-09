"""
Simple test runner that runs tests from the project root
"""
import os
import sys
import subprocess
from pathlib import Path

# Get project root
project_root = Path(__file__).parent

# Change to project root
os.chdir(project_root)

# Run test
test_file = sys.argv[1] if len(sys.argv) > 1 else "tests/test_token_fix.py"
result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
    
sys.exit(result.returncode)
