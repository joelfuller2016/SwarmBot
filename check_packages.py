"""Check if all required packages are installed"""

import subprocess
import sys

packages = [
    "openai",
    "anthropic", 
    "groq",
    "python-dotenv",
    "requests",
    "dash",
    "plotly"
]

print("[SwarmBot] Checking required packages...")
print("-" * 60)

missing = []
for package in packages:
    try:
        __import__(package.replace("-", "_"))
        print(f"[OK] {package}")
    except ImportError:
        print(f"[MISSING] {package}")
        missing.append(package)

if missing:
    print("\n[ACTION REQUIRED]")
    print("Install missing packages with:")
    print(f"pip install {' '.join(missing)}")
else:
    print("\n[SUCCESS] All packages installed!")
