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
import signal
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
        self.shutdown_event = asyncio.Event()
        self.chat_session = None
        
    def setup_environment(self):
        """Set up the environment for proper execution"""
        # Ensure UTF-8 encoding
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Set up proper asyncio event loop policy for Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print("\n[INFO] Received shutdown signal, cleaning up...")
            self.shutdown_event.set()
            # If we have a chat session, notify it
            if hasattr(self, 'chat_session') and self.chat_session:
                # Set a flag that the chat session can check
                self.chat_session._shutdown_requested = True
        
        # Register signal handlers
        if sys.platform == 'win32':
            # Windows signal handling
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            # Windows doesn't have SIGQUIT
        else:
            # Unix-like signal handling
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGQUIT, signal_handler)
    
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
            # Handle both 'servers' and 'mcpServers' keys for backward compatibility
            servers_dict = server_config.get('servers', server_config.get('mcpServers', {}))
            
            if not servers_dict:
                print("[WARNING] No servers configured in servers_config.json")
                return 0
            
            for name, srv_config in servers_dict.items():
                try:
                    server = Server(name, srv_config, self.config)
                    await server.initialize()
                    
                    tools = await server.list_tools()
                    if tools:
                        print(f"\n[{name}] ({len(tools)} tools):")
                        for tool in tools:
                            print(f"  - {tool.name}: {tool.description}")
                    else:
                        print(f"\n[{name}]: No tools available")
                    
                    await server.cleanup()
                except Exception as e:
                    print(f"\n[{name}]: Failed to initialize - {e}")
            
            # Give Windows ProactorEventLoop time to clean up transports
            if sys.platform == 'win32':
                await asyncio.sleep(0.5)
            
            return 0
            
        except Exception as e:
            print(f"\n[ERROR] Failed to list tools: {e}")
            return 1
    
    async def _cleanup_event_loop(self, loop) -> None:
        """Comprehensive cleanup of event loop resources to prevent asyncio errors on Windows."""
        # First, cleanup all servers (this handles subprocesses)
        if hasattr(self, 'servers') and self.servers:
            cleanup_tasks = []
            for server in self.servers:
                if hasattr(server, 'cleanup'):
                    cleanup_tasks.append(server.cleanup())
            
            if cleanup_tasks:
                try:
                    # Give servers time to cleanup with a reasonable timeout
                    await asyncio.wait_for(
                        asyncio.gather(*cleanup_tasks, return_exceptions=True),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    print("[WARNING] Server cleanup timed out")
                except Exception as e:
                    print(f"[WARNING] Error during server cleanup: {e}")
        
        # Cancel all remaining tasks
        try:
            # Get all pending tasks
            try:
                pending = asyncio.all_tasks(loop)
            except AttributeError:
                # Python 3.6 compatibility
                pending = asyncio.Task.all_tasks(loop)
            
            # Cancel them
            for task in pending:
                if not task.done() and task != asyncio.current_task():
                    task.cancel()
            
            # Wait for all tasks to complete cancellation
            if pending:
                await asyncio.wait(pending, timeout=5.0)
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.debug(f"Error cancelling tasks: {e}")
            else:
                print(f"[DEBUG] Error cancelling tasks: {e}")

        # Special handling for Windows ProactorEventLoop
        if sys.platform == 'win32':
            # Give time for subprocess transports to close properly
            await asyncio.sleep(0.5)
            
            # Force cleanup of any remaining transports
            if hasattr(loop, '_transports'):
                transports = list(loop._transports)
                for transport in transports:
                    try:
                        transport.close()
                    except Exception:
                        pass
            
            # Additional sleep to ensure all I/O operations complete
            await asyncio.sleep(0.2)
        
        # Final cleanup of any remaining tasks
        try:
            # Get remaining tasks one more time
            try:
                remaining = [t for t in asyncio.all_tasks(loop) if not t.done() and t != asyncio.current_task()]
            except AttributeError:
                remaining = [t for t in asyncio.Task.all_tasks(loop) if not t.done()]
            
            if remaining:
                for task in remaining:
                    task.cancel()
                await asyncio.wait(remaining, timeout=2.0)
        except Exception:
            pass

    async def run_chat_session(self, mode: str, args: argparse.Namespace) -> None:
        """Run the main chat session"""
        from src.chat_session import ChatSession
        
        # Configure logging based on mode
        log_file = 'logs/swarmbot.log' if mode == 'standard' else 'logs/swarmbot_enhanced.log'
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
            # Handle both 'servers' and 'mcpServers' keys for backward compatibility
            servers_dict = server_config.get('servers', server_config.get('mcpServers', {}))
            
            for name, srv_config in servers_dict.items():
                self.servers.append(Server(name, srv_config, self.config))

            # Create LLM client
            llm_client = LLMClient(self.config.llm_provider, self.config.llm_api_key)

            # Create appropriate chat session based on mode
            if mode == 'standard':
                chat_session = ChatSession(self.servers, llm_client, self.config)
            else:
                from src.enhanced_chat_session import EnhancedChatSession
                chat_session = EnhancedChatSession(self.servers, llm_client, self.config)
            
            # Store reference for signal handler
            self.chat_session = chat_session
                
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
        
        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()
        
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
            try:
                # Use asyncio.run for cleaner event loop management
                return asyncio.run(self.list_tools())
            except KeyboardInterrupt:
                return 0
            except Exception as e:
                print(f"[ERROR] Failed to list tools: {e}")
                return 1

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
            # Cleanup phase - ensure all resources are properly released
            print("\n[INFO] Shutting down SwarmBot...")
            
            # Run comprehensive cleanup
            try:
                loop.run_until_complete(self._cleanup_event_loop(loop))
            except Exception as e:
                print(f"[WARNING] Error during cleanup: {e}")
            
            # Close the loop
            try:
                loop.close()
            except Exception:
                pass
                
            print("[INFO] Cleanup completed.")