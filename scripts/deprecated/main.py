"""
SwarmBot - Standard Mode Entry Point
DEPRECATED: This file now redirects to unified_main.py
"""

import sys
import subprocess

print("ℹ️  main.py is deprecated. Using unified_main.py in standard mode...")
print()

# Run unified_main.py in standard mode
subprocess.run([sys.executable, 'unified_main.py', 'standard'] + sys.argv[1:])
