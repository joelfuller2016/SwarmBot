"""
SwarmBot - MCP Multi-Server Client Package
"""

__version__ = "1.0.0"
__author__ = "SwarmBot Team"

from .config import Configuration
from .server import Server
from .tool import Tool
from .llm_client import LLMClient, LLMProvider
from .chat_session import ChatSession
from .enhanced_chat_session import EnhancedChatSession
from .tool_matcher import ToolMatcher, ToolMatch
from .logging_utils import configure_logging, MCPNotificationFilter

__all__ = [
    "Configuration",
    "Server",
    "Tool",
    "LLMClient",
    "LLMProvider",
    "ChatSession",
    "EnhancedChatSession",
    "ToolMatcher",
    "ToolMatch",
    "configure_logging",
    "MCPNotificationFilter"
]
