"""
Chat Session module for SwarmBot
Orchestrates the interaction between user, LLM, and tools
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any

from .server import Server
from .tool import Tool
from .llm_client import LLMClient
from .core.commands import CommandParser
from .core.context_manager import ConversationContext
from .core.user_feedback import LoadingIndicator, ErrorFormatter, StatusDisplay

logger = logging.getLogger(__name__)


class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""

    def __init__(self, servers: List[Server], llm_client: LLMClient, config=None) -> None:
        self.servers: List[Server] = servers
        self.llm_client: LLMClient = llm_client
        self.active_servers: List[Server] = []
        self.all_tools: List[Tool] = []
        self.conversation_history: List[Dict[str, str]] = []
        self.config = config
        
        # NEW: Add command parser and context manager
        self.command_parser = CommandParser()
        # Pass max_context_tokens from config if available
        if config and hasattr(config, 'max_context_tokens'):
            self.context_manager = ConversationContext(max_tokens=config.max_context_tokens)
        else:
            self.context_manager = ConversationContext()
        self.error_formatter = ErrorFormatter()
        
        # For database logging
        self.db_logger = None  # Will be initialized in start()

    async def initialize_servers(self) -> None:
        """Initialize all configured servers."""
        logger.info("Initializing MCP servers...")
        
        initialization_tasks = []
        for server in self.servers:
            initialization_tasks.append(server.initialize())
        
        results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        for server, result in zip(self.servers, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to initialize {server.name}: {result}")
            elif result:
                self.active_servers.append(server)
                logger.info(f"Successfully initialized {server.name}")
            else:
                logger.warning(f"Server {server.name} failed to initialize")
        
        logger.info(f"Initialized {len(self.active_servers)} out of {len(self.servers)} servers")

    async def load_tools(self) -> None:
        """Load tools from all active servers."""
        logger.info("Loading tools from active servers...")
        
        for server in self.active_servers:
            tools = await server.list_tools()
            self.all_tools.extend(tools)
        
        logger.info(f"Loaded {len(self.all_tools)} tools total")

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly."""
        logger.info("Cleaning up servers...")
        
        if not self.servers:
            return
            
        # Give servers time to finish any pending operations
        await asyncio.sleep(0.1)
        
        cleanup_tasks = []
        for server in self.servers:
            if hasattr(server, 'session') and server.session:
                cleanup_tasks.append(server.cleanup())
            elif hasattr(server, 'stdio_context') and server.stdio_context:
                cleanup_tasks.append(server.cleanup())
        
        if cleanup_tasks:
            # Use shield to protect cleanup from cancellation
            try:
                await asyncio.wait_for(
                    asyncio.gather(*cleanup_tasks, return_exceptions=True),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning("Server cleanup timed out")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        
        # Give processes time to terminate
        await asyncio.sleep(0.1)
        logger.info("Server cleanup completed")

    def format_tool_result(self, tool_name: str, result: Any) -> str:
        """Format tool execution result for display."""
        if isinstance(result, dict):
            if 'error' in result:
                return f"❌ Error: {result['error']}"
            elif 'progress' in result and 'total' in result:
                progress = result['progress']
                total = result['total']
                percentage = (progress / total) * 100 if total > 0 else 0
                return f"📊 Progress: {progress}/{total} ({percentage:.1f}%)\n{result.get('data', '')}"
            else:
                return json.dumps(result, indent=2)
        elif isinstance(result, list):
            return json.dumps(result, indent=2)
        else:
            return str(result)

    async def process_llm_response(self, llm_response: str) -> str:
        """Process the LLM response and execute tools if needed."""
        try:
            # Try to parse as JSON for tool calls
            tool_call = json.loads(llm_response)
            
            if "tool" in tool_call and "arguments" in tool_call:
                tool_name = tool_call["tool"]
                arguments = tool_call["arguments"]
                
                logger.info(f"Tool call detected: {tool_name}")
                
                # Find server with the tool
                for server in self.active_servers:
                    tools = await server.list_tools()
                    if any(tool.name == tool_name for tool in tools):
                        success, result = await server.execute_tool(tool_name, arguments)
                        
                        if success:
                            formatted_result = self.format_tool_result(tool_name, result)
                            return f"✅ Tool '{tool_name}' executed successfully:\n\n{formatted_result}"
                        else:
                            return f"❌ Tool '{tool_name}' execution failed: {result}"
                
                return f"⚠️ Tool '{tool_name}' not found in any active server"
            
            return llm_response
            
        except json.JSONDecodeError:
            # Not a tool call, return as-is
            return llm_response
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return f"❌ Error processing response: {str(e)}"

    def build_system_prompt(self) -> str:
        """Build the system prompt with available tools."""
        tools_description = "\n\n".join([tool.format_for_llm() for tool in self.all_tools])
        
        return f"""You are SwarmBot, an intelligent assistant with access to multiple specialized tools through MCP (Model Context Protocol) servers.

Available Tools:
{tools_description}

Instructions:
1. When a user asks something that requires using a tool, respond ONLY with a JSON object in this exact format:
   {{
       "tool": "exact-tool-name",
       "arguments": {{
           "param1": "value1",
           "param2": "value2"
       }}
   }}

2. If no tool is needed, respond naturally and conversationally.

3. Choose the most appropriate tool based on the user's request.

4. Always use the exact tool name and parameter names as shown above.

5. After receiving a tool's response, provide a helpful summary or explanation of the results.

Remember: You have access to {len(self.all_tools)} tools across {len(self.active_servers)} active servers. Use them wisely to help the user."""

    async def start(self) -> None:
        """Main chat session handler."""
        # Show welcome with new status display
        StatusDisplay.show_welcome(self)
        
        try:
            # Initialize servers
            with LoadingIndicator("Initializing servers"):
                await self.initialize_servers()
            
            if not self.active_servers:
                print("\n❌ No servers could be initialized. Exiting.")
                return
            
            # Load tools
            with LoadingIndicator("Loading tools"):
                await self.load_tools()
            
            # Initialize context with system prompt
            system_prompt = self.build_system_prompt()
            self.context_manager.add_message("system", system_prompt)
            
            # Initialize database logger
            from .database.chat_storage import ChatDatabase, ChatLogger
            db = ChatDatabase()
            session_id = f"session_{int(time.time())}"
            db.create_session(session_id, self.llm_client.provider_name)
            self.db_logger = ChatLogger(db, session_id)
            
            print(f"\n✅ Ready! {StatusDisplay.format_status_line(self)}")
            print("-" * 60)
            
            while True:
                try:
                    user_input = input("\n🧑 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Check for commands first
                    context = {'chat_session': self}
                    command_result = self.command_parser.parse(user_input, context)
                    
                    if command_result:
                        # Handle command result
                        if command_result['type'] == 'exit':
                            print(command_result['message'])
                            break
                        elif command_result['type'] == 'delegate':
                            # Call existing method
                            method = getattr(self, command_result['method'])
                            method()
                        elif command_result['type'] == 'reset':
                            print(command_result['message'])
                            confirm = input("🧑 You: ").strip().lower()
                            if confirm == 'confirm':
                                self.context_manager.clear()
                                print("✅ Context reset successfully")
                        else:
                            print(command_result['message'])
                        continue
                    
                    # Log user message
                    if self.db_logger:
                        self.db_logger.log_user_message(user_input)
                    
                    # Add to context
                    self.context_manager.add_message("user", user_input)
                    
                    # Get LLM response with loading indicator
                    
                    
                    try:
                        with LoadingIndicator(""):
                            # Get context for LLM
                            messages = self.context_manager.get_context_for_llm()
                            llm_response = self.llm_client.get_response(messages, conversation_id=session_id)
                    except Exception as e:
                        error_msg = self.error_formatter.format_error(e)
                        print(f"\n❌ {error_msg}")
                        logger.error(f"LLM error: {e}", exc_info=True)
                        continue
                    
                    # Process response (check for tool calls)
                    result = await self.process_llm_response(llm_response)
                    
                    if result != llm_response:
                        # Tool was called
                        print(f"\n🔧 Tool Result: {result}")
                        
                        # Add both to history and context
                        self.conversation_history.append({"role": "assistant", "content": llm_response})
                        self.conversation_history.append({"role": "system", "content": f"Tool result: {result}"})
                        self.context_manager.add_message("assistant", llm_response)
                        self.context_manager.add_message("system", f"Tool result: {result}")
                        
                        # Get final response
                        messages = self.context_manager.get_context_for_llm()
                        final_response = self.llm_client.get_response(messages, conversation_id=session_id)
                        print(f"\n🤖 SwarmBot: {final_response}")
                        self.conversation_history.append({"role": "assistant", "content": final_response})
                        self.context_manager.add_message("assistant", final_response)
                    else:
                        # Regular response
                        print(f"\n🤖 SwarmBot: {llm_response}")
                        self.conversation_history.append({"role": "assistant", "content": llm_response})
                        self.context_manager.add_message("assistant", llm_response)
                    
                    # Log assistant response
                    if self.db_logger:
                        self.db_logger.log_assistant_message(result if result != llm_response else llm_response)
                
                except KeyboardInterrupt:
                    print("\n\n⚠️  Use 'quit' to exit properly.")
                except Exception as e:
                    error_msg = self.error_formatter.format_error(e)
                    print(f"\n❌ {error_msg}")
                    logger.error(f"Chat loop error: {e}", exc_info=True)
        
        finally:
            # End session in database
            if self.db_logger:
                self.db_logger.db.end_session(session_id)
            
            await self.cleanup_servers()

    def show_help(self) -> None:
        """Show help information."""
        print("\n📚 Available Commands:")
        print("  help    - Show this help message")
        print("  tools   - List all available tools")
        print("  servers - Show active servers")
        print("  quit    - Exit the application")

    def show_tools(self) -> None:
        """Show available tools."""
        print(f"\n🔧 Available Tools ({len(self.all_tools)}):")
        for i, tool in enumerate(self.all_tools, 1):
            print(f"\n{i}. {tool.name}")
            print(f"   {tool.description}")

    def show_servers(self) -> None:
        """Show active servers."""
        print(f"\n🖥️  Active Servers ({len(self.active_servers)}):")
        for server in self.active_servers:
            print(f"  - {server.name}")