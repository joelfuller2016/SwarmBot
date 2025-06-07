"""
SwarmBot - Unified Entry Point
Combines standard and enhanced modes into a single file
"""

import asyncio
import logging
import sys
import os
import warnings

# Suppress resource warnings on Windows
if sys.platform == 'win32':
    warnings.filterwarnings("ignore", category=ResourceWarning)
    # Set UTF-8 encoding for Windows console
    os.system('chcp 65001 > nul 2>&1')

# Import from src modules
from src.config import Configuration
from src.server import Server
from src.chat_session import ChatSession
from src.enhanced_chat_session import EnhancedChatSession
from src.llm_client import LLMClient
from src.logging_utils import configure_logging


async def main(mode: str = 'enhanced') -> None:
    """Initialize and run the chat session in specified mode.
    
    Args:
        mode: Either 'standard' or 'enhanced' mode
    """
    # Configure logging based on mode
    log_file = 'swarmbot.log' if mode == 'standard' else 'swarmbot_enhanced.log'
    logger = configure_logging(log_file)
    
    try:
        # Load configuration
        config = Configuration()
        server_config = config.load_config('config/servers_config.json')

        # Create servers
        servers = []
        for name, srv_config in server_config['mcpServers'].items():
            servers.append(Server(name, srv_config, config))

        # Create LLM client
        llm_client = LLMClient(config.llm_provider, config.llm_api_key)

        # Create appropriate chat session based on mode
        if mode == 'standard':
            chat_session = ChatSession(servers, llm_client)
        else:
            chat_session = EnhancedChatSession(servers, llm_client)
            
        await chat_session.start()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Parse command line argument for mode
    mode = 'enhanced'  # Default to enhanced mode
    if len(sys.argv) > 1:
        if sys.argv[1] in ['standard', 'enhanced']:
            mode = sys.argv[1]
        else:
            print(f"Invalid mode: {sys.argv[1]}. Use 'standard' or 'enhanced'")
            sys.exit(1)
    
    # Set up proper asyncio event loop policy for Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        # Create and run event loop manually for better control
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(main(mode))
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
            loop.call_soon_threadsafe(loop.stop)
            loop.run_forever()
            loop.close()

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        print(f"\n❌ Unhandled error: {str(e)}")
        sys.exit(1)
