#!/usr/bin/env python3
"""
Install script for SwarmBot WebSocket dependencies
Ensures all required packages are properly installed
"""

import subprocess
import sys
import importlib

def install_requirements():
    """Install all requirements from requirements.txt"""
    print("=" * 50)
    print("Installing SwarmBot WebSocket Dependencies")
    print("=" * 50)
    print()
    
    # Upgrade pip
    print("Updating pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install requirements
    print("\nInstalling all requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("\nVerifying installations...")
    
    # Packages to verify
    packages = [
        ("flask", "Flask"),
        ("flask_socketio", "Flask-SocketIO"),
        ("socketio", "python-socketio"),
        ("engineio", "python-engineio"),
        ("eventlet", "eventlet"),
        ("dash", "Dash"),
        ("plotly", "Plotly"),
        ("pytest", "pytest")
    ]
    
    all_installed = True
    
    for module_name, display_name in packages:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "unknown")
            print(f"✓ {display_name} version: {version}")
        except ImportError:
            print(f"✗ {display_name} not installed")
            all_installed = False
    
    print("\n" + "=" * 50)
    
    if all_installed:
        print("✅ All dependencies installed successfully!")
        print("\nYou can now run the WebSocket tests:")
        print("  python tests\\test_websocket_suite.py")
    else:
        print("❌ Some dependencies failed to install.")
        print("Please check the error messages above.")
    
    print("=" * 50)
    
    return all_installed

if __name__ == "__main__":
    success = install_requirements()
    sys.exit(0 if success else 1)
