"""
Chat Session module for SwarmBot
Orchestrates the interaction between user, LLM, and tools
"""

import asyncio
import json
import logging
from typing import List, Dict, Any

from .server import Server
from .tool import Tool
from .llm_client import LLMClient

logger = logging.getLogger(__name__)


class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""

    def __init__(self, servers: List[Server], llm_client: LLMClient) -> None:
        self.servers: List[Server] = servers
        self.llm_client: LLMClient = llm_client
        self.active_servers: List[Server] = []
        self.all_tools: List[Tool] = []
        self.conversation_history: List[Dict[str, str]] = []

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
        print("\n🚀 SwarmBot MCP Client")
        print("=" * 50)
        
        try:
            # Initialize servers
            await self.initialize_servers()
            
            if not self.active_servers:
                print("\n❌ No servers could be initialized. Exiting.")
                return
            
            # Load tools
            await self.load_tools()
            
            if not self.all_tools:
                print("\n⚠️  No tools available, but continuing with conversation mode.")
            
            # Build system prompt
            system_message = {
                "role": "system",
                "content": self.build_system_prompt()
            }
            
            self.conversation_history = [system_message]
            
            print(f"\n✅ Initialized with {len(self.active_servers)} servers and {len(self.all_tools)} tools")
            print("\n💬 Type 'help' for available commands, 'quit' to exit")
            print("=" * 50)
            
            while True:
                try:
                    user_input = input("\n🧑 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("\n👋 Goodbye!")
                        break
                    
                    if user_input.lower() == 'help':
                        self.show_help()
                        continue
                    
                    if user_input.lower() == 'tools':
                        self.show_tools()
                        continue
                    
                    if user_input.lower() == 'servers':
                        self.show_servers()
                        continue
                    
                    # Add user message to history
                    self.conversation_history.append({"role": "user", "content": user_input})
                    
                    # Get LLM response
                    print("\n🤖 SwarmBot: ", end="", flush=True)
                    llm_response = self.llm_client.get_response(self.conversation_history)
                    
                    # Process response (check for tool calls)
                    result = await self.process_llm_response(llm_response)
                    
                    if result != llm_response:
                        # Tool was called
                        print(result)
                        
                        # Add both to history
                        self.conversation_history.append({"role": "assistant", "content": llm_response})
                        self.conversation_history.append({"role": "system", "content": f"Tool result: {result}"})
                        
                        # Get final response
                        final_response = self.llm_client.get_response(self.conversation_history)
                        print(f"\n🤖 SwarmBot: {final_response}")
                        self.conversation_history.append({"role": "assistant", "content": final_response})
                    else:
                        # Regular response
                        print(llm_response)
                        self.conversation_history.append({"role": "assistant", "content": llm_response})
                
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrupted. Type 'quit' to exit properly.")
                except Exception as e:
                    logger.error(f"Error in chat loop: {e}")
                    print(f"\n❌ Error: {str(e)}")
        
        finally:
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