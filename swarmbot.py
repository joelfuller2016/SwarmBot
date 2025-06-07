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
            issues.append("⚠️  No .env file found. Please create one with your API keys.")
        
        # Check for required files
        for mode_info in self.modes.values():
            if not Path(mode_info['script']).exists():
                issues.append(f"❌ Missing required file: {mode_info['script']}")
        
        # Check for servers config
        if not Path('config/servers_config.json').exists():
            issues.append("❌ Missing config/servers_config.json")
        
        if issues:
            print("\n🚨 Setup Issues Found:")
            for issue in issues:
                print(f"   {issue}")
            print("\nPlease resolve these issues before running SwarmBot.")
            return False
            
        return True
    
    def interactive_mode_selection(self):
        """Interactive mode selection with detailed information"""
        print("\n🤖 SwarmBot Mode Selection")
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
                input("\nPress Enter to continue...")
                return self.interactive_mode_selection()
            elif choice == '4':
                return None
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    def show_help(self):
        """Show detailed help information"""
        print("\n📚 SwarmBot Help")
        print("=" * 60)
        print()
        print("Usage: python swarmbot.py [mode] [options]")
        print()
        print("Modes:")
        print("  standard    - Run in standard mode (manual tool execution)")
        print("  enhanced    - Run in enhanced mode (automatic tool detection)")
        print("  auto        - Alias for enhanced mode")
        print()
        print("Options:")
        print("  --help, -h  - Show this help message")
        print("  --check     - Check requirements without running")
        print("  --clean     - Clean log files before starting")
        print()
        print("Examples:")
        print("  python swarmbot.py              # Interactive mode selection")
        print("  python swarmbot.py enhanced     # Start in enhanced mode")
        print("  python swarmbot.py --check      # Check setup")
        print()
        print("Environment:")
        print("  Create a .env file with your API keys:")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")
        print("  - GITHUB_PERSONAL_ACCESS_TOKEN")
        print("  - etc.")
    
    def clean_logs(self):
        """Clean old log files"""
        log_files = ['swarmbot.log', 'swarmbot_enhanced.log']
        cleaned = 0
        
        for log_file in log_files:
            if Path(log_file).exists():
                try:
                    Path(log_file).unlink()
                    cleaned += 1
                except Exception as e:
                    print(f"⚠️  Could not delete {log_file}: {e}")
        
        if cleaned > 0:
            print(f"✅ Cleaned {cleaned} log file(s)")
    
    def run(self, mode):
        """Run SwarmBot in the specified mode"""
        if mode not in self.modes:
            print(f"❌ Invalid mode: {mode}")
            return 1
        
        mode_info = self.modes[mode]
        script = mode_info['script']
        
        print(f"\n🚀 Starting SwarmBot")
        print(f"Mode: {mode_info['description']}")
        print(f"Script: {script}")
        print(f"Log: {mode_info['log_file']}")
        print("=" * 60)
        print()
        
        env = self.setup_environment()
        
        try:
            # Run the script with mode argument
            result = subprocess.run(
                [sys.executable, script, mode],
                env=env,
                check=False
            )
            
            # Small delay for cleanup
            time.sleep(0.5)
            
            return result.returncode
            
        except KeyboardInterrupt:
            print("\n\n👋 SwarmBot terminated by user")
            return 0
        except Exception as e:
            print(f"\n❌ Error running SwarmBot: {e}")
            return 1
    
    def main(self):
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description='SwarmBot Unified Launcher',
            add_help=False
        )
        
        parser.add_argument(
            'mode',
            nargs='?',
            choices=['standard', 'enhanced', 'auto'],
            help='Mode to run SwarmBot in'
        )
        
        parser.add_argument(
            '--help', '-h',
            action='store_true',
            help='Show help message'
        )
        
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check requirements without running'
        )
        
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean log files before starting'
        )
        
        args = parser.parse_args()
        
        # Show header
        print("\n🤖 SwarmBot - MCP Multi-Server Client")
        print("=" * 60)
        
        # Handle help
        if args.help:
            self.show_help()
            return 0
        
        # Check requirements
        if args.check or not self.check_requirements():
            return 0 if args.check else 1
        
        # Clean logs if requested
        if args.clean:
            self.clean_logs()
        
        # Determine mode
        if args.mode:
            mode = args.mode
        else:
            mode = self.interactive_mode_selection()
            if mode is None:
                print("\n👋 Goodbye!")
                return 0
        
        # Run SwarmBot
        return self.run(mode)


if __name__ == "__main__":
    launcher = SwarmBotLauncher()
    sys.exit(launcher.main())
