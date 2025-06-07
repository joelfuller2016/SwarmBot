"""
Server module for SwarmBot
Manages MCP server connections and tool execution
"""

import asyncio
import logging
import shutil
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import InitializeResult

from .tool import Tool
from .config import Configuration

logger = logging.getLogger(__name__)


class Server:
    """Manages MCP server connections and tool execution."""

    def __init__(self, name: str, config: Dict[str, Any], global_config: Configuration) -> None:
        self.name: str = name
        self.config: Dict[str, Any] = config
        self.global_config: Configuration = global_config
        self.stdio_context: Optional[Any] = None
        self.session: Optional[ClientSession] = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.capabilities: Optional[InitializeResult] = None
        self._initialization_attempts: int = 0
        self._max_initialization_attempts: int = 3

    async def initialize(self) -> bool:
        """Initialize the server connection with retry logic."""
        while self._initialization_attempts < self._max_initialization_attempts:
            try:
                self._initialization_attempts += 1
                logger.info(f"Initializing server {self.name} (attempt {self._initialization_attempts})")
                
                # Get command path
                command = self.config['command']
                if command in ["npx", "uvx"]:
                    command_path = shutil.which(command) or command
                else:
                    command_path = command

                # Prepare environment
                env = self.global_config.get_server_env(self.config)

                server_params = StdioServerParameters(
                    command=command_path,
                    args=self.config.get('args', []),
                    env=env
                )
                
                self.stdio_context = stdio_client(server_params)
                read, write = await self.stdio_context.__aenter__()
                self.session = ClientSession(read, write)
                await self.session.__aenter__()
                self.capabilities = await self.session.initialize()
                
                logger.info(f"Successfully initialized server {self.name}")
                return True
                
            except Exception as e:
                logger.error(f"Error initializing server {self.name}: {e}")
                await self.cleanup()
                
                if self._initialization_attempts < self._max_initialization_attempts:
                    await asyncio.sleep(2 ** self._initialization_attempts)
                else:
                    logger.error(f"Failed to initialize server {self.name} after {self._max_initialization_attempts} attempts")
                    return False
        
        return False

    async def list_tools(self) -> List[Tool]:
        """List available tools from the server."""
        if not self.session:
            logger.warning(f"Server {self.name} not initialized")
            return []
        
        try:
            tools_response = await self.session.list_tools()
            tools = []
            
            supports_progress = (
                self.capabilities 
                and hasattr(self.capabilities, 'progress')
                and self.capabilities.progress
            )
            
            if supports_progress:
                logger.debug(f"Server {self.name} supports progress tracking")
            
            for item in tools_response:
                if isinstance(item, tuple) and item[0] == 'tools':
                    for tool in item[1]:
                        tools.append(Tool(tool.name, tool.description, tool.inputSchema))
                        if supports_progress:
                            logger.debug(f"Tool '{tool.name}' supports progress tracking")
            
            logger.info(f"Found {len(tools)} tools in server {self.name}")
            return tools
            
        except Exception as e:
            logger.error(f"Error listing tools from server {self.name}: {e}")
            return []

    async def execute_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any], 
        retries: int = 2, 
        delay: float = 1.0
    ) -> Tuple[bool, Any]:
        """Execute a tool with retry mechanism."""
        if not self.session:
            return False, f"Server {self.name} not initialized"

        attempt = 0
        last_error = None
        
        while attempt < retries:
            try:
                supports_progress = (
                    self.capabilities 
                    and hasattr(self.capabilities, 'progress')
                    and self.capabilities.progress
                )

                logger.info(f"Executing {tool_name} on server {self.name} (attempt {attempt + 1})")
                
                if supports_progress:
                    result = await self.session.call_tool(
                        tool_name, 
                        arguments,
                        progress_token=f"{tool_name}_execution_{datetime.now().timestamp()}"
                    )
                else:
                    result = await self.session.call_tool(tool_name, arguments)

                logger.info(f"Successfully executed {tool_name}")
                return True, result

            except Exception as e:
                last_error = e
                attempt += 1
                logger.warning(f"Error executing tool {tool_name}: {e}. Attempt {attempt} of {retries}.")
                
                if attempt < retries:
                    await asyncio.sleep(delay * attempt)
                else:
                    logger.error(f"Failed to execute {tool_name} after {retries} attempts")
        
        return False, f"Tool execution failed: {last_error}"

    async def cleanup(self) -> None:
        """Clean up server resources."""
        async with self._cleanup_lock:
            try:
                if self.session:
                    try:
                        await self.session.__aexit__(None, None, None)
                    except Exception as e:
                        logger.debug(f"Session cleanup for {self.name}: {e}")
                    finally:
                        self.session = None

                if self.stdio_context:
                    try:
                        await self.stdio_context.__aexit__(None, None, None)
                    except (RuntimeError, asyncio.CancelledError) as e:
                        logger.debug(f"Normal shutdown for {self.name}: {e}")
                    except Exception as e:
                        logger.warning(f"Unexpected error during stdio cleanup for {self.name}: {e}")
                    finally:
                        self.stdio_context = None
                        
                logger.info(f"Cleaned up server {self.name}")
                
            except Exception as e:
                logger.error(f"Critical error during cleanup of server {self.name}: {e}")