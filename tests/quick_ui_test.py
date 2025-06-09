#!/usr/bin/env python3
"""Quick UI test to check basic functionality"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing SwarmBot UI components...")
print("-" * 40)

# Test 1: Basic imports
try:
    import dash
    print("✓ Dash is installed")
except ImportError:
    print("✗ Dash is NOT installed - run: pip install dash")

try:
    import plotly
    print("✓ Plotly is installed")
except ImportError:
    print("✗ Plotly is NOT installed - run: pip install plotly")

try:
    import dash_bootstrap_components
    print("✓ Dash Bootstrap Components is installed")
except ImportError:
    print("✗ Dash Bootstrap Components is NOT installed - run: pip install dash-bootstrap-components")

try:
    import flask_socketio
    print("✓ Flask-SocketIO is installed")
except ImportError:
    print("✗ Flask-SocketIO is NOT installed - run: pip install flask-socketio")

print("\n" + "-" * 40)

# Test 2: SwarmBot imports
try:
    from src.config import Configuration
    print("✓ Configuration module imports successfully")
    
    # Try to create config
    config = Configuration()
    print("✓ Configuration instance created")
except Exception as e:
    print(f"✗ Configuration module error: {e}")

try:
    from src.ui.dash.integration import SwarmBotDashboard
    print("✓ SwarmBotDashboard imports successfully")
except Exception as e:
    print(f"✗ SwarmBotDashboard import error: {e}")

try:
    from src.ui.dash import create_app
    print("✓ Dash app module imports successfully")
except Exception as e:
    print(f"✗ Dash app import error: {e}")

print("\n" + "-" * 40)
print("Test complete. Fix any errors shown above.")
