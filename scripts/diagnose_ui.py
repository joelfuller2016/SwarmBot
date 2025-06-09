#!/usr/bin/env python3
"""
Comprehensive UI Diagnostic Tool for SwarmBot Dashboard
Checks all prerequisites, imports, and configurations
"""

import sys
import os
from pathlib import Path
import importlib.util
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8+ required")
        return False
    print("✓ Python version OK")
    return True

def check_project_structure():
    """Check if required directories exist"""
    print_header("Project Structure Check")
    required_dirs = [
        'src',
        'src/ui',
        'src/ui/dash',
        'src/core',
        'src/agents',
        'config',
        'logs'
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ NOT FOUND")
            all_exist = False
    
    return all_exist

def check_required_files():
    """Check if required files exist"""
    print_header("Required Files Check")
    required_files = [
        'src/ui/dash/integration.py',
        'src/ui/dash/app.py',
        'src/ui/dash/layouts.py',
        'src/ui/dash/callbacks.py',
        'src/core/test_runner_service.py',
        'config/servers_config.json',
        '.env'
    ]
    
    all_exist = True
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✓ {file_name} exists")
        else:
            print(f"✗ {file_name} NOT FOUND")
            all_exist = False
    
    return all_exist

def check_imports():
    """Check if all imports work"""
    print_header("Import Check")
    
    imports_to_check = [
        ('dash', 'dash'),
        ('plotly', 'plotly'),
        ('dash_bootstrap_components', 'dash-bootstrap-components'),
        ('flask_socketio', 'flask-socketio'),
        ('src.config', 'Configuration module'),
        ('src.agents', 'Agents module'),
        ('src.ui.dash.app', 'Dash app module'),
        ('src.ui.dash.integration', 'Dashboard integration')
    ]
    
    all_success = True
    for import_name, display_name in imports_to_check:
        try:
            if '.' in import_name:
                parts = import_name.split('.')
                module = __import__('.'.join(parts[:-1]), fromlist=[parts[-1]])
            else:
                __import__(import_name)
            print(f"✓ {display_name} imports successfully")
        except ImportError as e:
            print(f"✗ {display_name} FAILED: {str(e)}")
            all_success = False
        except Exception as e:
            print(f"✗ {display_name} ERROR: {type(e).__name__}: {str(e)}")
            all_success = False
    
    return all_success

def check_configuration():
    """Check configuration files"""
    print_header("Configuration Check")
    
    # Check servers_config.json
    config_path = project_root / 'config' / 'servers_config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✓ servers_config.json is valid JSON")
            # Handle both 'servers' and 'mcpServers' keys for backward compatibility
            servers_dict = config.get('servers', config.get('mcpServers', {}))
            if servers_dict:
                print(f"✓ Found {len(servers_dict)} MCP servers configured")
            else:
                print("✗ No servers section in config")
        except json.JSONDecodeError as e:
            print(f"✗ servers_config.json is invalid: {e}")
            return False
    else:
        print("✗ servers_config.json not found")
        return False
    
    # Check .env file
    env_path = project_root / '.env'
    if env_path.exists():
        print("✓ .env file exists")
        # Check for API keys
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')
        }
        
        found_keys = [k for k, v in api_keys.items() if v]
        if found_keys:
            print(f"✓ Found API keys: {', '.join(found_keys)}")
        else:
            print("✗ No LLM API keys found in .env")
    else:
        print("✗ .env file not found")
    
    return True

def test_dashboard_import():
    """Test importing the dashboard"""
    print_header("Dashboard Import Test")
    
    try:
        from src.ui.dash.integration import SwarmBotDashboard
        print("✓ SwarmBotDashboard imported successfully")
        
        # Try to instantiate
        try:
            dashboard = SwarmBotDashboard()
            print("✓ SwarmBotDashboard instantiated successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to instantiate SwarmBotDashboard: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import SwarmBotDashboard: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")
        return False

def generate_report(results):
    """Generate a summary report"""
    print_header("Diagnostic Summary")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    print(f"\nTotal checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    
    if passed_checks == total_checks:
        print("\n✓ All checks passed! The UI should work correctly.")
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nFailed checks:")
        for check, result in results.items():
            if not result:
                print(f"  - {check}")

def main():
    """Run all diagnostics"""
    print("\n" + "=" * 60)
    print(" " * 10 + "[SwarmBot UI Diagnostic Tool]")
    print("=" * 60)
    
    results = {}
    
    # Run all checks
    results['Python Version'] = check_python_version()
    results['Project Structure'] = check_project_structure()
    results['Required Files'] = check_required_files()
    results['Package Imports'] = check_imports()
    results['Configuration'] = check_configuration()
    results['Dashboard Import'] = test_dashboard_import()
    
    # Generate report
    generate_report(results)
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
