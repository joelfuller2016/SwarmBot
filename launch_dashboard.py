#!/usr/bin/env python3
"""
Launch script to start SwarmBot with UI dashboard directly
This bypasses the circular import issue
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

print("\n" + "=" * 60)
print(" " * 20 + "[SwarmBot Dashboard]")
print(" " * 10 + "Starting Web Interface")
print("=" * 60 + "\n")

try:
    # Import and run the dashboard directly
    from src.ui.dash.integration import main
    main()
except ImportError as e:
    print(f"[ERROR] Failed to import dashboard: {e}")
    print("\nMake sure all dependencies are installed:")
    print("  pip install dash plotly dash-bootstrap-components dash-extensions psutil")
except KeyboardInterrupt:
    print("\n[INFO] Dashboard terminated by user.")
except Exception as e:
    print(f"[ERROR] Failed to launch dashboard: {e}")
    import traceback
    traceback.print_exc()
