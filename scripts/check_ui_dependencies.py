#!/usr/bin/env python3
"""
Check and install UI dependencies for SwarmBot Dashboard
"""

import sys
import subprocess
import importlib.util

def check_package(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def main():
    print("\n" + "=" * 60)
    print(" " * 15 + "[SwarmBot UI Dependency Checker]")
    print("=" * 60 + "\n")
    
    # List of required packages
    required_packages = {
        'dash': 'dash',
        'plotly': 'plotly',
        'dash_bootstrap_components': 'dash-bootstrap-components',
        'dash_extensions': 'dash-extensions',
        'psutil': 'psutil',
        'flask_socketio': 'flask-socketio',
        'python-socketio': 'python-socketio',
        'eventlet': 'eventlet'
    }
    
    missing_packages = []
    installed_packages = []
    
    # Check each package
    for import_name, pip_name in required_packages.items():
        if check_package(import_name):
            installed_packages.append(import_name)
            print(f"✓ {import_name} is installed")
        else:
            missing_packages.append(pip_name)
            print(f"✗ {import_name} is NOT installed")
    
    print("\n" + "-" * 60)
    
    if missing_packages:
        print(f"\n[WARNING] {len(missing_packages)} packages are missing!")
        print("\nTo install missing packages, run:")
        print(f"  pip install {' '.join(missing_packages)}")
        
        response = input("\nWould you like to install them now? (y/n): ")
        if response.lower() == 'y':
            print("\n[INFO] Installing missing packages...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
                print("\n[SUCCESS] All packages installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"\n[ERROR] Failed to install packages: {e}")
                return 1
    else:
        print("\n[SUCCESS] All UI dependencies are installed!")
    
    # Check versions
    print("\n" + "-" * 60)
    print("\n[INFO] Installed package versions:")
    for import_name in installed_packages:
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'Unknown')
            print(f"  {import_name}: {version}")
        except:
            print(f"  {import_name}: (version unknown)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
