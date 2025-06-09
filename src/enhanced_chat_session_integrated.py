"""
Enhanced Chat Session with integrated chat history database and error logging
This shows how to integrate the new features into the existing chat session
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any
from datetime import datetime

from .server import Server
from .tool import Tool
from .llm_client import LLMClient
from .database import ChatDatabase, ChatLogger
from .utils.logging_config import LoggingMixin, log_async_errors

logger = logging.getLogger(__name__)


class EnhancedChatSession(LoggingMixin):
    """Enhanced chat session with database logging and error tracking"""

    def __init__(self, servers: List[Server], llm_client: LLMClient, db_path: str = "data/swarmbot_chats.db"):
        self.servers: List[Server] = servers
        self.llm_client: LLMClient = llm_client
        self.active_servers: List[Server] = []
        self.all_tools: List[Tool] = []
        self.conversation_history: List[Dict[str, str]] = []
        
        # Initialize database and logger
        self.db = ChatDatabase(db_path)
        self.session_id = f"session_{datetime.now().timestamp()}"
        self.chat_logger = None
        
        # Initialize session
        self._init_session()

    def _init_session(self):
        """Initialize the chat session in database"""
        self.db.create_session(
            self.session_id,
            self.llm_client.provider,
            {
                "started_at": datetime.utcnow().isoformat(),
                "servers": [s.name for s in self.servers]
            }
        )
        self.chat_logger = ChatLogger(self.db, self.session_id)
        self.log_info("Chat session initialized", session_id=self.session_id)

    @log_async_errors()
    async def initialize_servers(self) -> None:
        """Initialize all configured servers with error logging"""
        self.log_info("Initializing MCP servers...")

        initialization_tasks = []
        for server in self.servers:
            initialization_tasks.append(server.initialize())

        results = await asyncio.gather(*initialization_tasks, return_exceptions=True)

        for server, result in zip(self.servers, results):
            if isinstance(result, Exception):
                self.log_error(f"Failed to initialize {server.name}", 
                             exc_info=result, server=server.name)
            elif result:
                self.active_servers.append(server)
                self.log_info(f"Successfully initialized {server.name}")
            else:
                self.log_warning(f"Server {server.name} failed to initialize")

        self.log_info(f"Initialized {len(self.active_servers)} out of {len(self.servers)} servers")

    @log_async_errors()
    async def load_tools(self) -> None:
        """Load tools from all active servers with logging"""
        self.log_info("Loading tools from active servers...")

        for server in self.active_servers:
            try:
                tools = await server.list_tools()
                self.all_tools.extend(tools)
                self.log_debug(f"Loaded {len(tools)} tools from {server.name}")
            except Exception as e:
                self.log_error(f"Failed to load tools from {server.name}", 
                             exc_info=True, server=server.name)

        self.log_info(f"Loaded {len(self.all_tools)} tools total")

    async def process_message(self, user_input: str) -> str:
        """Process a user message with full logging"""
        # Log user message
        user_msg_id = self.chat_logger.log_user_message(user_input, {
            "timestamp": datetime.utcnow().isoformat(),
            "conversation_length": len(self.conversation_history)
        })
        
        self.log_info("Processing user message", message_id=user_msg_id)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})

        try:
            # Get LLM response with tool calls
            response = await self._get_llm_response_with_tools(user_input, user_msg_id)
            
            # Log assistant response
            assistant_msg_id = self.chat_logger.log_assistant_message(response, {
                "model": self.llm_client.model,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            self.log_info("Message processed successfully", 
                         user_msg_id=user_msg_id,
                         assistant_msg_id=assistant_msg_id)
            
            return response
            
        except Exception as e:
            self.log_error("Failed to process message", 
                         exc_info=True,
                         user_msg_id=user_msg_id)
            raise

    async def _get_llm_response_with_tools(self, user_input: str, msg_id: str) -> str:
        """Get LLM response, handling tool calls with logging"""
        # This is a simplified example - actual implementation would be more complex
        
        # Log MCP request
        self.chat_logger.log_mcp_request(
            "llm", "chat.completion", 
            {"messages": self.conversation_history[-10:]}  # Last 10 messages
        )
        
        start_time = time.time()
        
        try:
            # Get LLM response
            response = await self.llm_client.get_response(
                self.conversation_history,
                tools=self.all_tools
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log MCP response
            self.chat_logger.log_mcp_response(
                "llm", "chat.completion", 
                {"response": response[:200]}  # First 200 chars
            )
            
            # Check for tool calls in response
            if hasattr(response, 'tool_calls'):
                for tool_call in response.tool_calls:
                    await self._execute_tool_with_logging(
                        tool_call, msg_id
                    )
            
            return response.content
            
        except Exception as e:
            self.log_error("LLM request failed", exc_info=True)
            raise

    async def _execute_tool_with_logging(self, tool_call: Any, msg_id: str):
        """Execute a tool call with full logging"""
        tool_name = tool_call.name
        tool_args = tool_call.arguments
        
        # Find the tool
        tool = next((t for t in self.all_tools if t.name == tool_name), None)
        if not tool:
            self.log_error(f"Tool not found: {tool_name}")
            return
        
        # Log MCP tool request
        self.chat_logger.log_mcp_request(
            tool.server_name, tool_name, tool_args
        )
        
        start_time = time.time()
        
        try:
            # Execute tool
            result = await tool.execute(tool_args)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log successful tool call
            self.chat_logger.log_tool_call(
                msg_id, tool_name, tool.server_name,
                tool_args, result, duration_ms
            )
            
            # Log MCP tool response
            self.chat_logger.log_mcp_response(
                tool.server_name, tool_name, result
            )
            
            self.log_info(f"Tool {tool_name} executed successfully",
                         duration_ms=duration_ms)
            
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log failed tool call
            self.chat_logger.log_tool_call(
                msg_id, tool_name, tool.server_name,
                tool_args, None, duration_ms,
                status="error", error_message=str(e)
            )
            
            self.log_error(f"Tool {tool_name} failed",
                         exc_info=True,
                         tool=tool_name,
                         duration_ms=duration_ms)
            raise

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly with logging"""
        self.log_info("Cleaning up servers...")

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
                self.log_warning("Server cleanup timed out")
            except Exception as e:
                self.log_error("Error during cleanup", exc_info=True)

        # Give processes time to terminate
        await asyncio.sleep(0.1)
        
        # End database session
        self.db.end_session(self.session_id)
        
        self.log_info("Server cleanup completed")

    def export_session(self, output_path: str = None):
        """Export the current session to a file"""
        if not output_path:
            output_path = f"session_{self.session_id}.json"
        
        self.db.export_session(self.session_id, output_path)
        self.log_info(f"Session exported to {output_path}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session"""
        messages = self.db.get_session_messages(self.session_id)
        
        tool_calls = []
        for msg in messages:
            tools = self.db.get_message_tools(msg['message_id'])
            tool_calls.extend(tools)
        
        return {
            "session_id": self.session_id,
            "message_count": len(messages),
            "tool_call_count": len(tool_calls),
            "duration": (datetime.utcnow() - datetime.fromisoformat(
                messages[0]['timestamp'] if messages else datetime.utcnow().isoformat()
            )).total_seconds(),
            "active_servers": len(self.active_servers),
            "total_tools": len(self.all_tools)
        }


# Example usage
if __name__ == "__main__":
    from src.config import Configuration
    from src.server import Server
    from src.llm_client import LLMClient
    
    async def test_enhanced_session():
        # Setup
        config = Configuration()
        servers = []  # Load your servers here
        llm_client = LLMClient(config)
        
        # Create enhanced session
        session = EnhancedChatSession(servers, llm_client)
        
        try:
            # Initialize
            await session.initialize_servers()
            await session.load_tools()
            
            # Process a message
            response = await session.process_message("What's the weather like?")
            print(f"Response: {response}")
            
            # Get session summary
            summary = session.get_session_summary()
            print(f"Session summary: {json.dumps(summary, indent=2)}")
            
            # Export session
            session.export_session()
            
        finally:
            # Cleanup
            await session.cleanup_servers()
    
    # Run test
    asyncio.run(test_enhanced_session())
