#!/usr/bin/env python3
"""
UI Status Check and Launch Instructions
"""

import sys
import os
from pathlib import Path
import subprocess

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n" + "=" * 60)
print(" " * 15 + "SwarmBot UI Status Check")
print("=" * 60 + "\n")

# Check 1: Python version
print("[1] Python Version:")
print(f"    Current: {sys.version}")
if sys.version_info >= (3, 8):
    print("    ✓ Python version OK")
else:
    print("    ✗ Python 3.8+ required")

# Check 2: Check if .env exists and has API keys
print("\n[2] Configuration:")
env_path = project_root / ".env"
if env_path.exists():
    print("    ✓ .env file exists")
    content = env_path.read_text()
    if "your-" in content or "=" not in content:
        print("    ⚠ Warning: .env may contain placeholder values")
        print("    Action: Edit .env and add your actual API keys")
else:
    print("    ✗ .env file missing")
    print("    Action: Copy .env.example to .env and add your API keys")

# Check 3: UI Dependencies
print("\n[3] UI Dependencies:")
deps = {
    "dash": "pip install dash",
    "plotly": "pip install plotly", 
    "dash_bootstrap_components": "pip install dash-bootstrap-components",
    "flask_socketio": "pip install flask-socketio"
}

missing = []
for module, install_cmd in deps.items():
    try:
        __import__(module)
        print(f"    ✓ {module} installed")
    except ImportError:
        print(f"    ✗ {module} NOT installed")
        missing.append(install_cmd)

# Check 4: SwarmBot imports
print("\n[4] SwarmBot Module Imports:")
try:
    from src.ui.dash.integration import SwarmBotDashboard
    print("    ✓ SwarmBotDashboard imports successfully")
except Exception as e:
    print(f"    ✗ SwarmBotDashboard import failed: {e}")

# Instructions
print("\n" + "=" * 60)
print(" LAUNCH INSTRUCTIONS")
print("=" * 60)

if missing:
    print("\n1. Install missing dependencies:")
    for cmd in missing:
        print(f"   {cmd}")
    print("\n2. Or install all at once:")
    print("   pip install dash plotly dash-bootstrap-components flask-socketio")

print("\n3. Launch the UI using one of these methods:")
print("\n   Method A (Recommended - includes checks):")
print("   > fix_and_launch_ui.bat")
print("\n   Method B (Direct launch):")
print("   > python swarmbot.py --ui")
print("\n   Method C (Alternative launcher):")
print("   > python launch_dashboard.py")

print("\n4. The UI will be available at:")
print("   http://127.0.0.1:8050")

print("\n" + "=" * 60)
print(" QUICK FIX COMMANDS")
print("=" * 60)
print("\nIf you encounter issues, run these in order:")
print("\n1. Check dependencies:")
print("   > python check_ui_dependencies.py")
print("\n2. Run diagnostics:")
print("   > python diagnose_ui.py")
print("\n3. Apply fixes and launch:")
print("   > fix_and_launch_ui.bat")

print("\n" + "=" * 60 + "\n")
