#!/usr/bin/env python3
"""
SwarmBot Core Application
Main application logic for SwarmBot - modular and extensible
"""

import asyncio
import logging
import sys
import os
import warnings
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Suppress resource warnings on Windows
if sys.platform == 'win32':
    warnings.filterwarnings("ignore", category=ResourceWarning)
    # Set UTF-8 encoding for Windows console
    os.system('chcp 65001 > nul 2>&1')

# Import from src modules
from src.config import Configuration
from src.server import Server
from src.chat_session import ChatSession
from src.llm_client import LLMClient
from src.logging_utils import configure_logging


class SwarmBotApp:
    """Main application class for SwarmBot"""
    
    def __init__(self):
        """Initialize the SwarmBot application"""
        self.config = None
        self.servers = []
        self.logger = None
        self.mode = 'enhanced'  # Default mode
        
    def setup_environment(self):
        """Set up the environment for proper execution"""
        # Ensure UTF-8 encoding
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Set up proper asyncio event loop policy for Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='SwarmBot - AI Assistant with MCP Tools',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Modes:
  standard    Manual tool execution with full control
  enhanced    Automatic tool detection from natural language (default)

Examples:
  swarmbot                    # Run in enhanced mode (default)
  swarmbot standard           # Run in standard mode
  swarmbot --validate         # Validate configuration only
  swarmbot --list-tools       # List available tools
  swarmbot --clean-logs       # Clean old log files
            """
        )
        
        parser.add_argument(
            'mode',
            nargs='?',
            choices=['standard', 'enhanced'],
            default='enhanced',
            help='Mode to run SwarmBot in'
        )
        
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate configuration and exit'
        )
        
        parser.add_argument(
            '--list-tools',
            action='store_true',
            help='List available tools and exit'
        )
        
        parser.add_argument(
            '--clean-logs',
            action='store_true',
            help='Clean old log files and exit'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging'
        )

        parser.add_argument(
            '--ui',
            action='store_true',
            help='Launch the dashboard interface instead of chat mode'
        )
        
        parser.add_argument(
            '--no-validation',
            action='store_true',
            help='Skip configuration validation'
        )
        
        # Auto-prompt arguments
        parser.add_argument(
            '--auto-prompt',
            action='store_true',
            help='Enable auto-prompt functionality (override .env setting)'
        )
        
        parser.add_argument(
            '--no-auto-prompt',
            action='store_true',
            help='Disable auto-prompt functionality (override .env setting)'
        )
        
        parser.add_argument(
            '--auto-prompt-iterations',
            type=int,
            metavar='N',
            help='Maximum auto-prompt iterations (default: from .env or 1)'
        )
        
        return parser.parse_args(args)
    
    def clean_logs(self) -> int:
        """Clean old log files"""
        log_files = list(Path('.').glob('*.log'))
        cleaned = 0
        
        for log_file in log_files:
            try:
                log_file.unlink()
                cleaned += 1
                print(f"[CLEANED] {log_file}")
            except Exception as e:
                print(f"[WARNING] Could not delete {log_file}: {e}")
        
        print(f"\n[OK] Cleaned {cleaned} log file(s)")
        return 0
    
    def validate_configuration(self) -> bool:
        """Validate the configuration"""
        print("[SwarmBot] Validating configuration...")
        print("=" * 60)
        
        # Basic validation checks
        issues = []
        
        # Check for .env file
        if not Path('.env').exists():
            issues.append("[WARNING] No .env file found")
        
        # Check for required directories
        required_dirs = ['config', 'src', 'src/agents', 'src/ui', 'logs']
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                issues.append(f"[ERROR] Missing directory: {dir_name}")
        
        # Check for config files
        if not Path('config/servers_config.json').exists():
            issues.append("[ERROR] Missing config/servers_config.json")
        
        # Check for at least one LLM API key
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')
        }
        
        if not any(api_keys.values()):
            issues.append("[ERROR] No LLM API keys found (need at least one)")
        
        # Print validation results
        if issues:
            print("\n[Validation Issues]")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n[OK] Configuration is valid!")
        
        print("\n" + "=" * 60)
        
        # Return True if no errors (warnings are OK)
        return not any("[ERROR]" in issue for issue in issues)
    
    async def list_tools(self) -> int:
        """List all available tools from configured servers"""
        try:
            # Load configuration
            self.config = Configuration()
            server_config = self.config.load_config('config/servers_config.json')
            
            print("[SwarmBot] Available Tools")
            print("=" * 60)
            
            # Create servers temporarily to get tool lists
            for name, srv_config in server_config['mcpServers'].items():
                try:
                    server = Server(name, srv_config, self.config)
                    await server.initialize()
                    
                    tools = await server.list_tools()
                    if tools:
                        print(f"\n[{name}] ({len(tools)} tools):")
                        for tool in tools:
                            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
                    else:
                        print(f"\n[{name}]: No tools available")
                    
                    await server.cleanup()
                except Exception as e:
                    print(f"\n[{name}]: Failed to initialize - {e}")
            
            return 0
            
        except Exception as e:
            print(f"\n[ERROR] Failed to list tools: {e}")
            return 1
    
    async def run_chat_session(self, mode: str, args: argparse.Namespace) -> None:
        """Run the main chat session"""
        # Configure logging based on mode
        log_file = 'swarmbot.log' if mode == 'standard' else 'swarmbot_enhanced.log'
        self.logger = configure_logging(log_file)
        
        try:
            # Load configuration
            self.config = Configuration()
            server_config = self.config.load_config('config/servers_config.json')
            
            # Apply command-line overrides for auto-prompt
            if args.auto_prompt:
                self.config.auto_prompt_enabled = True
                print("[CONFIG] Auto-prompt enabled via command line")
            elif args.no_auto_prompt:
                self.config.auto_prompt_enabled = False
                print("[CONFIG] Auto-prompt disabled via command line")
            
            if args.auto_prompt_iterations is not None:
                self.config.auto_prompt_max_iterations = args.auto_prompt_iterations
                print(f"[CONFIG] Auto-prompt iterations set to {args.auto_prompt_iterations}")

            # Create servers
            self.servers = []
            for name, srv_config in server_config['mcpServers'].items():
                self.servers.append(Server(name, srv_config, self.config))

            # Create LLM client
            llm_client = LLMClient(self.config.llm_provider, self.config.llm_api_key)

            # Create appropriate chat session based on mode
            if mode == 'standard':
                chat_session = ChatSession(self.servers, llm_client)
            else:
                from src.enhanced_chat_session import EnhancedChatSession
                chat_session = EnhancedChatSession(self.servers, llm_client)
                
            # Start the chat session
            await chat_session.start()

        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            print(f"\n[ERROR] Fatal error: {str(e)}")
            raise
    
    def run(self, args: List[str]) -> int:
        """Main run method"""
        # Setup environment
        self.setup_environment()
        
        # Parse arguments
        parsed_args = self.parse_arguments(args)
        
        # Handle special commands
        if parsed_args.clean_logs:
            return self.clean_logs()
        
        # Print header
        print("\n" + "=" * 60)
        print(" " * 20 + "[SwarmBot]")
        print(" " * 10 + "AI Assistant with MCP Tools")
        print("=" * 60 + "\n")
        
        # Validate configuration unless skipped
        if not parsed_args.no_validation:
            if not self.validate_configuration():
                if not parsed_args.validate:
                    print("\n[WARNING] Configuration has issues but continuing...")
                else:
                    return 1
        
        # Exit if only validating
        if parsed_args.validate:
            return 0
        
        # Handle list tools
        if parsed_args.list_tools:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.list_tools())
            finally:
                loop.close()

        # Handle UI mode
        if parsed_args.ui:
            print("[SwarmBot] Launching dashboard interface...")
            print("-" * 60 + "\n")
            
            # Import and run the dashboard
            try:
                from src.ui.dash.integration import SwarmBotDashboard
                dashboard = SwarmBotDashboard(self.config)
                dashboard.run(debug=parsed_args.debug)
                return 0
            except ImportError as e:
                print(f"[ERROR] Failed to import dashboard: {e}")
                print("Make sure Dash and Plotly are installed: pip install dash plotly dash-bootstrap-components")
                return 1
            except Exception as e:
                print(f"[ERROR] Failed to launch dashboard: {e}")
                if parsed_args.debug:
                    import traceback
                    traceback.print_exc()
                return 1
        
        # Run the main chat session
        print(f"[SwarmBot] Starting in {parsed_args.mode} mode...")
        print("-" * 60 + "\n")
        
        # Create and run event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.run_chat_session(parsed_args.mode, parsed_args))
            return 0
            
        except KeyboardInterrupt:
            print("\n\n[INFO] SwarmBot terminated by user.")
            return 0
            
        except Exception as e:
            print(f"\n[ERROR] Unhandled error: {e}")
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 1
            
        finally:
            # Cleanup phase
            try:
                pending = asyncio.all_tasks(loop)
            except AttributeError:
                # Python 3.9+ uses asyncio.all_tasks()
                pending = asyncio.tasks.all_tasks(loop)

            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            # Give time for cleanup
            loop.run_until_complete(asyncio.sleep(0.5))

            # Close the loop
            try:
                loop.close()
            except Exception:
                pass  # Ignore cleanup errors