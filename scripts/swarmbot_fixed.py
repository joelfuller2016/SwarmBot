#!/usr/bin/env python3
"""
SwarmBot Unified Launcher
Single entry point for all SwarmBot modes and configurations
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path


class SwarmBotLauncher:
    """Unified launcher for SwarmBot with all modes and options"""
    
    def __init__(self):
        self.modes = {
            'standard': {
                'script': 'unified_main.py',
                'description': 'Standard mode with manual tool execution',
                'log_file': 'swarmbot.log'
            },
            'enhanced': {
                'script': 'unified_main.py',
                'description': 'Enhanced mode with automatic tool detection',
                'log_file': 'swarmbot_enhanced.log'
            },
            'auto': {
                'script': 'enhanced_main.py',
                'description': 'Alias for enhanced mode',
                'log_file': 'swarmbot_enhanced.log'
            }
        }
        
    def setup_environment(self):
        """Set up environment variables and encoding"""
        env = os.environ.copy()
        env['PYTHONWARNINGS'] = 'ignore::ResourceWarning'
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Set UTF-8 mode for Windows
        if sys.platform == 'win32':
            os.system('chcp 65001 > nul 2>&1')
            
        return env
    
    def check_requirements(self):
        """Check if all requirements are met"""
        issues = []
        
        # Check for .env file
        if not Path('.env').exists():
            issues.append("[WARNING] No .env file found. Please create one with your API keys.")
        
        # Check for required files
        for mode_info in self.modes.values():
            if not Path(mode_info['script']).exists():
                issues.append(f"[ERROR] Missing required file: {mode_info['script']}")
        
        # Check for servers config
        if not Path('config/servers_config.json').exists():
            issues.append("[ERROR] Missing config/servers_config.json")
        
        if issues:
            print("\n[!] Setup Issues Found:")
            for issue in issues:
                print(f"   {issue}")
            print("\nPlease resolve these issues before running SwarmBot.")
            return False
            
        return True
    
    def interactive_mode_selection(self):
        """Interactive mode selection with detailed information"""
        print("\n[SwarmBot] Mode Selection")
        print("=" * 60)
        print()
        print("Available modes:")
        print()
        print("1. Standard Mode")
        print("   - Manual tool execution with full control")
        print("   - You explicitly call tools using JSON format")
        print("   - Best for: Learning, debugging, precise control")
        print()
        print("2. Enhanced Mode (Recommended)")
        print("   - Automatic tool detection from natural language")
        print("   - Intelligent tool chaining and execution")
        print("   - Best for: Productivity, natural interaction")
        print()
        print("3. Help")
        print("   - Show command-line usage and options")
        print()
        print("4. Exit")
        print()
        
        while True:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                return 'standard'
            elif choice == '2':
                return 'enhanced'
            elif choice == '3':
                self.show_help()
                return None
            elif choice == '4':
                print("\nExiting SwarmBot.")
                return None
            else:
                print("Invalid choice. Please enter 1-4.")
    
    def show_help(self):
        """Show help information"""
        print("\n[SwarmBot] Help")
        print("=" * 60)
        print()
        print("Usage: python swarmbot.py [mode] [options]")
        print()
        print("Modes:")
        print("  standard    Standard mode with manual tool execution")
        print("  enhanced    Enhanced mode with automatic tool detection (default)")
        print("  auto        Alias for enhanced mode")
        print()
        print("Options:")
        print("  -h, --help        Show this help message")
        print("  --clean-logs      Clean up old log files")
        print("  --no-check        Skip requirement checks")
        print("  --debug           Enable debug logging")
        print()
        print("Examples:")
        print("  python swarmbot.py              # Interactive mode selection")
        print("  python swarmbot.py enhanced     # Start in enhanced mode")
        print("  python swarmbot.py standard     # Start in standard mode")
        print("  python swarmbot.py --clean-logs # Clean log files")
        print()
        input("Press Enter to continue...")
    
    def clean_logs(self):
        """Clean up old log files"""
        log_files = list(Path('.').glob('*.log'))
        cleaned = 0
        
        for log_file in log_files:
            try:
                log_file.unlink()
                cleaned += 1
            except Exception as e:
                print(f"[WARNING] Could not delete {log_file}: {e}")
        
        if cleaned > 0:
            print(f"[OK] Cleaned {cleaned} log file(s)")
        else:
            print("[INFO] No log files to clean")
    
    def run_mode(self, mode, debug=False):
        """Run SwarmBot in the specified mode"""
        if mode not in self.modes:
            print(f"[ERROR] Invalid mode: {mode}")
            self.show_help()
            return 1
        
        mode_info = self.modes[mode]
        script = mode_info['script']
        
        if not Path(script).exists():
            print(f"[ERROR] Script not found: {script}")
            return 1
        
        # Set up environment
        env = self.setup_environment()
        
        # Set mode environment variable
        env['SWARMBOT_MODE'] = 'enhanced' if mode in ['enhanced', 'auto'] else 'standard'
        
        # Set debug flag if requested
        if debug:
            env['SWARMBOT_DEBUG'] = '1'
        
        # Log file setup
        log_file = mode_info['log_file']
        env['SWARMBOT_LOG'] = log_file
        
        print(f"\n[SwarmBot] Starting in {mode} mode...")
        print(f"[INFO] Log file: {log_file}")
        print("-" * 60)
        
        # Run the script
        try:
            result = subprocess.run(
                [sys.executable, script],
                env=env,
                check=False
            )
            return result.returncode
        except KeyboardInterrupt:
            print("\n\n[INFO] SwarmBot terminated by user.")
            return 0
        except Exception as e:
            print(f"\n[ERROR] Error running SwarmBot: {e}")
            return 1
    
    def main(self):
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description='SwarmBot - Unified AI Assistant with MCP Tools',
            add_help=False
        )
        
        parser.add_argument('mode', nargs='?', choices=['standard', 'enhanced', 'auto'],
                          help='Mode to run SwarmBot in')
        parser.add_argument('-h', '--help', action='store_true',
                          help='Show help message')
        parser.add_argument('--clean-logs', action='store_true',
                          help='Clean up old log files')
        parser.add_argument('--no-check', action='store_true',
                          help='Skip requirement checks')
        parser.add_argument('--debug', action='store_true',
                          help='Enable debug logging')
        
        args = parser.parse_args()
        
        # Handle help
        if args.help:
            self.show_help()
            return 0
        
        # Handle log cleaning
        if args.clean_logs:
            self.clean_logs()
            return 0
        
        # Print header
        print("\n" + "=" * 60)
        print(" " * 20 + "[SwarmBot]")
        print(" " * 10 + "AI Assistant with MCP Tools")
        print("=" * 60)
        
        # Check requirements unless skipped
        if not args.no_check and not self.check_requirements():
            return 1
        
        # Determine mode
        if args.mode:
            mode = args.mode
        else:
            mode = self.interactive_mode_selection()
            if mode is None:
                return 0
        
        # Run the selected mode
        return self.run_mode(mode, debug=args.debug)


if __name__ == "__main__":
    launcher = SwarmBotLauncher()
    sys.exit(launcher.main())
