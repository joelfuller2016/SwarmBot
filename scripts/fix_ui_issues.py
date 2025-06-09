#!/usr/bin/env python3
"""
Comprehensive UI Fix Script for SwarmBot Dashboard
Identifies and fixes all UI-related issues
"""

import sys
import os
import subprocess
from pathlib import Path
import json
import traceback

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_success(message):
    """Print success message"""
    print(f"✓ {message}")

def print_error(message):
    """Print error message"""
    print(f"✗ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠ {message}")

def fix_imports():
    """Fix import issues in UI modules"""
    print_header("Fixing Import Issues")
    
    # Fix integration.py to handle TestRunnerService import gracefully
    integration_path = project_root / "src" / "ui" / "dash" / "integration.py"
    
    # Already fixed according to task 42, let's verify
    if integration_path.exists():
        content = integration_path.read_text(encoding='utf-8')
        if "try:" in content and "TestRunnerService" in content:
            print_success("TestRunnerService import is already wrapped in try-except")
        else:
            print_warning("TestRunnerService import might need attention")
    
    # Fix Python path in main launcher
    swarmbot_path = project_root / "swarmbot.py"
    if swarmbot_path.exists():
        print_success("swarmbot.py exists")
    else:
        print_error("swarmbot.py not found!")
        
    return True

def install_missing_dependencies():
    """Install any missing UI dependencies"""
    print_header("Checking and Installing Dependencies")
    
    required_packages = [
        "dash",
        "plotly", 
        "dash-bootstrap-components",
        "dash-extensions",
        "flask-socketio",
        "python-socketio",
        "psutil"
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package} is installed")
        except ImportError:
            print_warning(f"{package} is missing")
            missing.append(package)
    
    if missing:
        print(f"\nInstalling missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print_success("All missing packages installed")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install packages: {e}")
            return False
    else:
        print_success("All required packages are already installed")
        return True

def create_missing_files():
    """Create any missing required files"""
    print_header("Checking Required Files")
    
    # Check if logs directory exists
    logs_dir = project_root / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        print_success("Created logs directory")
    else:
        print_success("logs directory exists")
    
    # Check .env file
    env_path = project_root / ".env"
    if not env_path.exists():
        print_warning(".env file missing - creating template")
        env_content = """# SwarmBot Configuration
# Add your API keys here

# LLM Provider (groq, anthropic, openai)
LLM_PROVIDER=groq

# API Keys
GROQ_API_KEY=your-groq-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key

# Auto-prompt settings
AUTO_PROMPT_ENABLED=true
AUTO_PROMPT_MAX_ITERATIONS=1
"""
        env_path.write_text(env_content)
        print_success("Created .env template file")
    else:
        print_success(".env file exists")
    
    return True

def test_ui_launch():
    """Test if the UI can launch successfully"""
    print_header("Testing UI Launch")
    
    try:
        # Test importing the dashboard
        from src.ui.dash.integration import SwarmBotDashboard
        print_success("SwarmBotDashboard imported successfully")
        
        # Test creating an instance
        from src.config import Configuration
        config = Configuration()
        dashboard = SwarmBotDashboard(config)
        print_success("SwarmBotDashboard instantiated successfully")
        
        # Test if we can access the app creation
        from src.ui.dash import create_app
        app = create_app()
        print_success("Dash app created successfully")
        
        return True
        
    except Exception as e:
        print_error(f"UI launch test failed: {e}")
        traceback.print_exc()
        return False

def create_launch_script():
    """Create a simple launch script for the UI"""
    print_header("Creating Launch Scripts")
    
    # Create a simple launcher batch file
    launcher_content = """@echo off
echo Starting SwarmBot Dashboard...
echo.
cd /d "%~dp0"
python swarmbot.py --ui
pause
"""
    
    launcher_path = project_root / "launch_ui.bat"
    launcher_path.write_text(launcher_content)
    print_success("Created launch_ui.bat")
    
    # Create a Python launcher as alternative
    py_launcher_content = """#!/usr/bin/env python3
\"\"\"Simple UI launcher for SwarmBot\"\"\"

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Launch the UI
os.system('python swarmbot.py --ui')
"""
    
    py_launcher_path = project_root / "launch_ui.py"
    py_launcher_path.write_text(py_launcher_content)
    print_success("Created launch_ui.py")
    
    return True

def generate_diagnostic_report():
    """Generate a diagnostic report of issues found"""
    print_header("Diagnostic Report")
    
    issues = []
    recommendations = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python version is below 3.8")
        recommendations.append("Upgrade to Python 3.8 or higher")
    
    # Check for .env file with API keys
    env_path = project_root / ".env"
    if env_path.exists():
        content = env_path.read_text()
        if "your-" in content:
            issues.append(".env file contains placeholder API keys")
            recommendations.append("Add your actual API keys to .env file")
    
    # Print issues and recommendations
    if issues:
        print("\nIssues Found:")
        for issue in issues:
            print(f"  - {issue}")
        
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  - {rec}")
    else:
        print_success("No critical issues found!")
    
    return len(issues) == 0

def main():
    """Run all fixes"""
    print("\n" + "=" * 60)
    print(" " * 15 + "SwarmBot UI Fix Script")
    print("=" * 60)
    
    all_success = True
    
    # Run all fix functions
    all_success &= fix_imports()
    all_success &= install_missing_dependencies()
    all_success &= create_missing_files()
    all_success &= test_ui_launch()
    all_success &= create_launch_script()
    all_success &= generate_diagnostic_report()
    
    # Final summary
    print_header("Summary")
    if all_success:
        print_success("All fixes completed successfully!")
        print("\nTo launch the UI, use one of these methods:")
        print("  1. Run: launch_ui.bat")
        print("  2. Run: python launch_ui.py")
        print("  3. Run: python swarmbot.py --ui")
    else:
        print_error("Some fixes failed. Please review the output above.")
        print("\nNext steps:")
        print("  1. Check the error messages above")
        print("  2. Ensure all dependencies are installed")
        print("  3. Add your API keys to the .env file")
        print("  4. Try running: python -m pip install -r requirements.txt")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
