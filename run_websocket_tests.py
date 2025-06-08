"""
WebSocket Test Runner Script
"""
import os
import sys
import subprocess

# Change to the SwarmBot directory
os.chdir(r'C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot')

# Add the directory to Python path
sys.path.insert(0, os.getcwd())

# Run the test suite
if __name__ == "__main__":
    try:
        result = subprocess.run([sys.executable, 'tests/test_websocket_suite.py'], 
                               capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)
