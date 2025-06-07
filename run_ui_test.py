import subprocess
import sys
import os

# Change to project directory
os.chdir(r"C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot")

# Run the test script
result = subprocess.run([sys.executable, "test_ui_comprehensive.py"], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")
