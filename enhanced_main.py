"""
SwarmBot - Enhanced Mode Entry Point
DEPRECATED: This file now redirects to unified_main.py
"""

import sys
import subprocess

print("ℹ️  enhanced_main.py is deprecated. Using unified_main.py in enhanced mode...")
print()

# Run unified_main.py in enhanced mode
subprocess.run([sys.executable, 'unified_main.py', 'enhanced'] + sys.argv[1:])
