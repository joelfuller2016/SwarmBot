#!/usr/bin/env python3
"""
SwarmBot Universal Launcher v3.0
Single entry point for all SwarmBot functions with automatic dependency management
Cross-platform launcher with comprehensive checks and diagnostics
"""

import sys
import os
import subprocess
import platform
import json
import importlib.util
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ANSI color codes for terminal output
if platform.system() == "Windows":
    os.system('color')  # Enable ANSI on Windows 10+
    # Set UTF-8 encoding
    os.system('chcp 65001 > nul 2>&1')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print the SwarmBot header"""
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}       SwarmBot - AI Assistant with MCP Tools{Colors.ENDC}")
    print(f"{Colors.HEADER}              Universal Launcher v3.0{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def check_python_version():
    """Check if Python version is 3.8+"""
    print(f"{Colors.BLUE}[1/5] Checking Python installation...{Colors.ENDC}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"{Colors.GREEN}      ✓ Python {version.major}.{version.minor}.{version.micro} installed{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}      ✗ Python 3.8+ required (found {version.major}.{version.minor}){Colors.ENDC}")
        return False

def read_requirements():
    """Read all required packages from requirements.txt"""
    requirements_path = project_root / "requirements.txt"
    packages = {}
    
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package name and version
                    if '>=' in line:
                        pkg_name = line.split('>=')[0].strip()
                    elif '==' in line:
                        pkg_name = line.split('==')[0].strip()
                    else:
                        pkg_name = line.strip()
                    
                    # Map pip names to import names
                    import_name = pkg_name.replace('-', '_')
                    if pkg_name == 'python-dotenv':
                        import_name = 'dotenv'
                    elif pkg_name == 'dash-bootstrap-components':
                        import_name = 'dash_bootstrap_components'
                    elif pkg_name == 'dash-extensions':
                        import_name = 'dash_extensions'
                    elif pkg_name == 'flask-socketio':
                        import_name = 'flask_socketio'
                    elif pkg_name == 'python-engineio':
                        import_name = 'engineio'
                    elif pkg_name == 'python-socketio':
                        import_name = 'socketio'
                    
                    packages[import_name] = pkg_name
    
    return packages

def check_package(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def check_and_install_dependencies():
    """Check and install all required dependencies"""
    print(f"\n{Colors.BLUE}[2/5] Checking dependencies...{Colors.ENDC}")
    
    # Get all required packages
    packages = read_requirements()
    
    # Add jsonschema if not in requirements
    if 'jsonschema' not in packages:
        packages['jsonschema'] = 'jsonschema'
    
    missing = []
    installed = []
    
    for import_name, pip_name in packages.items():
        if check_package(import_name):
            installed.append(import_name)
        else:
            missing.append(pip_name)
    
    print(f"      Found {len(installed)} installed packages, {len(missing)} missing")
    
    if missing:
        print(f"{Colors.YELLOW}      Missing packages: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}{Colors.ENDC}")
        print(f"{Colors.YELLOW}      Installing missing dependencies...{Colors.ENDC}")
        try:
            # Upgrade pip first
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Install missing packages
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + missing)
            print(f"{Colors.GREEN}      ✓ All dependencies installed successfully!{Colors.ENDC}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}      ✗ Failed to install dependencies!{Colors.ENDC}")
            print(f"{Colors.RED}      Error: {e}{Colors.ENDC}")
            print(f"{Colors.RED}      Please run manually: pip install -r requirements.txt{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.GREEN}      ✓ All dependencies are installed!{Colors.ENDC}")
        return True

def check_configuration():
    """Check environment configuration"""
    print(f"\n{Colors.BLUE}[3/5] Checking configuration...{Colors.ENDC}")
    
    env_path = project_root / ".env"
    env_example_path = project_root / ".env.example"
    
    if not env_path.exists():
        if env_example_path.exists():
            print(f"{Colors.YELLOW}      Creating .env from template...{Colors.ENDC}")
            env_path.write_text(env_example_path.read_text())
        else:
            print(f"{Colors.YELLOW}      Creating basic .env template...{Colors.ENDC}")
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
        print(f"{Colors.YELLOW}      ⚠ Please edit .env and add your API keys!{Colors.ENDC}")
    else:
        print(f"{Colors.GREEN}      ✓ Configuration file found!{Colors.ENDC}")
    
    # Check for valid API keys
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            'GROQ_API_KEY': os.getenv('GROQ_API_KEY', ''),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', '')
        }
        
        valid_keys = [k for k, v in api_keys.items() 
                     if v.strip() and not v.startswith('your-')]
        
        if not valid_keys:
            print(f"{Colors.YELLOW}      ⚠ No valid API keys found in .env!{Colors.ENDC}")
            print(f"{Colors.YELLOW}      Please add at least one API key to continue.{Colors.ENDC}")
            return False
        else:
            print(f"{Colors.GREEN}      ✓ Found API keys: {', '.join(valid_keys)}{Colors.ENDC}")
            return True
    except ImportError:
        return False

def check_ui_components():
    """Check UI-specific components and dependencies"""
    print(f"\n{Colors.BLUE}[4/5] Checking UI components...{Colors.ENDC}")
    
    ui_deps = {
        'dash': 'Dashboard framework',
        'plotly': 'Plotting library',
        'dash_bootstrap_components': 'UI components',
        'flask_socketio': 'WebSocket support',
        'eventlet': 'Async support'
    }
    
    all_good = True
    for module, desc in ui_deps.items():
        if check_package(module):
            print(f"{Colors.GREEN}      ✓ {desc} ({module}){Colors.ENDC}")
        else:
            print(f"{Colors.RED}      ✗ {desc} ({module}) missing{Colors.ENDC}")
            all_good = False
    
    return all_good

def run_diagnostics():
    """Run comprehensive diagnostics"""
    print(f"\n{Colors.BLUE}[5/5] Running diagnostics...{Colors.ENDC}")
    
    issues = []
    
    # Check core modules
    try:
        from src.config import Configuration
        print(f"{Colors.GREEN}      ✓ Configuration module OK{Colors.ENDC}")
    except Exception as e:
        issues.append(f"Configuration module: {e}")
    
    try:
        from src.core.app import SwarmBotApp
        print(f"{Colors.GREEN}      ✓ Core application module OK{Colors.ENDC}")
    except Exception as e:
        issues.append(f"Core app module: {e}")
    
    try:
        from src.ui.dash.integration import SwarmBotDashboard
        print(f"{Colors.GREEN}      ✓ Dashboard module OK{Colors.ENDC}")
    except Exception as e:
        issues.append(f"Dashboard module: {e}")
    
    # Check server configuration
    servers_config = project_root / "config" / "servers_config.json"
    if servers_config.exists():
        try:
            with open(servers_config, 'r') as f:
                json.load(f)
            print(f"{Colors.GREEN}      ✓ Server configuration valid{Colors.ENDC}")
        except Exception as e:
            issues.append(f"Server config: {e}")
    else:
        issues.append("Server configuration file missing")
    
    if issues:
        print(f"\n{Colors.YELLOW}      ⚠ Found {len(issues)} issues:{Colors.ENDC}")
        for issue in issues[:3]:  # Show first 3 issues
            print(f"{Colors.YELLOW}        - {issue}{Colors.ENDC}")
        if len(issues) > 3:
            print(f"{Colors.YELLOW}        ... and {len(issues) - 3} more{Colors.ENDC}")
        return False
    else:
        print(f"{Colors.GREEN}      ✓ All systems operational!{Colors.ENDC}")
        return True

def show_menu():
    """Show the main menu and get user choice"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("   Choose SwarmBot Launch Mode:")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    print("  1. 🌐 Dashboard UI (Web Interface)")
    print("  2. 🚀 Enhanced Chat (Auto-tools)")
    print("  3. 💬 Standard Chat (Manual tools)")
    print("  4. ✓  Validate Configuration")
    print("  5. 🛠️  List Available Tools")
    print("  6. 🔍 Run Full Diagnostics")
    print("  7. 🧹 Clean Logs")
    print("  8. ❌ Exit\n")
    
    while True:
        try:
            choice = input("Enter your choice (1-8): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return int(choice)
            else:
                print(f"{Colors.RED}Invalid choice! Please select 1-8.{Colors.ENDC}")
        except KeyboardInterrupt:
            return 8

def launch_ui():
    """Launch the dashboard UI"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("   🌐 Launching SwarmBot Dashboard...")
    print(f"{'='*60}{Colors.ENDC}\n")
    print("The dashboard will open at: http://127.0.0.1:8050")
    print("Press Ctrl+C to stop the server.\n")
    
    # Check if UI dependencies are OK
    if not check_ui_components():
        print(f"\n{Colors.RED}UI components are missing! Installing...{Colors.ENDC}")
        subprocess.run([sys.executable, "-m", "pip", "install", 
                       "dash", "plotly", "dash-bootstrap-components", 
                       "flask-socketio", "eventlet"])
    
    subprocess.run([sys.executable, "swarmbot.py", "--ui"])

def launch_enhanced():
    """Launch enhanced chat mode"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("   🚀 Launching Enhanced Chat Mode...")
    print(f"{'='*60}{Colors.ENDC}\n")
    print("Enhanced mode with automatic tool detection enabled.")
    print("Type 'exit' or press Ctrl+C to quit.\n")
    
    subprocess.run([sys.executable, "swarmbot.py", "enhanced"])

def launch_standard():
    """Launch standard chat mode"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("   💬 Launching Standard Chat Mode...")
    print(f"{'='*60}{Colors.ENDC}\n")
    print("Standard mode with manual tool control.")
    print("Type 'exit' or press Ctrl+C to quit.\n")
    
    subprocess.run([sys.executable, "swarmbot.py", "standard"])

def validate_config():
    """Validate configuration"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("   ✓ Validating Configuration...")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    subprocess.run([sys.executable, "swarmbot.py", "--validate"])
    input("\nPress Enter to continue...")

def list_tools():
    """List available tools"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("   🛠️  Available MCP Tools...")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    subprocess.run([sys.executable, "swarmbot.py", "--list-tools"])
    input("\nPress Enter to continue...")

def run_full_diagnostics():
    """Run full diagnostics"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("   🔍 Running Full Diagnostics...")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    # Run UI diagnostics if available
    diag_script = project_root / "scripts" / "diagnose_ui.py"
    if diag_script.exists():
        subprocess.run([sys.executable, str(diag_script)])
    
    # Run validation with debug
    subprocess.run([sys.executable, "swarmbot.py", "--validate", "--debug"])
    
    input("\nPress Enter to continue...")

def clean_logs():
    """Clean log files"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("   🧹 Cleaning Log Files...")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    subprocess.run([sys.executable, "swarmbot.py", "--clean-logs"])
    input("\nPress Enter to continue...")

def main():
    """Main launcher function"""
    # Clear screen
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    # Print header
    print_header()
    
    # Run initial checks
    if not check_python_version():
        print(f"\n{Colors.RED}Please install Python 3.8 or higher from https://python.org{Colors.ENDC}")
        input("\nPress Enter to exit...")
        return 1
    
    if not check_and_install_dependencies():
        input("\nPress Enter to exit...")
        return 1
    
    config_ok = check_configuration()
    diag_ok = run_diagnostics()
    
    if not config_ok:
        print(f"\n{Colors.YELLOW}⚠ Configuration issues detected. Please add API keys to .env{Colors.ENDC}")
    
    if not diag_ok:
        print(f"\n{Colors.YELLOW}⚠ Some components may have issues. Run diagnostics for details.{Colors.ENDC}")
    
    # Main loop
    while True:
        choice = show_menu()
        
        if choice == 1:
            launch_ui()
            break
        elif choice == 2:
            launch_enhanced()
            break
        elif choice == 3:
            launch_standard()
            break
        elif choice == 4:
            validate_config()
            os.system('cls' if platform.system() == 'Windows' else 'clear')
            print_header()
        elif choice == 5:
            list_tools()
            os.system('cls' if platform.system() == 'Windows' else 'clear')
            print_header()
        elif choice == 6:
            run_full_diagnostics()
            os.system('cls' if platform.system() == 'Windows' else 'clear')
            print_header()
        elif choice == 7:
            clean_logs()
            os.system('cls' if platform.system() == 'Windows' else 'clear')
            print_header()
        elif choice == 8:
            print(f"\n{Colors.GREEN}SwarmBot session ended. Goodbye! 👋{Colors.ENDC}")
            break
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}SwarmBot terminated by user.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
