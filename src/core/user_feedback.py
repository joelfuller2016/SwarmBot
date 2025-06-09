"""
User feedback and display utilities for SwarmBot
Provides loading indicators, error formatting, and status displays
"""

import sys
import time
import threading
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LoadingIndicator:
    """Simple loading indicator for CLI"""
    
    def __init__(self, message: str = "Thinking"):
        self.message = message
        self.running = False
        self.thread = None
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_frame = 0
    
    def _animate(self):
        """Animation loop"""
        while self.running:
            frame = self.frames[self.current_frame]
            print(f"\r{frame} {self.message}...", end="", flush=True)
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            time.sleep(0.1)
    
    def start(self):
        """Start the loading indicator"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._animate, daemon=True)
            self.thread.start()
    
    def stop(self, final_message: str = ""):
        """Stop the loading indicator"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        print(f"\r{' ' * (len(self.message) + 10)}\r", end="", flush=True)
        if final_message:
            print(final_message)
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


class ErrorFormatter:
    """Formats errors for user-friendly display"""
    
    # Error message mappings
    ERROR_MESSAGES = {
        # Connection errors
        "ConnectionError": "Unable to connect to AI service. Please check your internet connection.",
        "TimeoutError": "Request timed out. The service might be busy.",
        "SSLError": "Secure connection failed. Please check your network settings.",
        
        # API errors
        "AuthenticationError": "Invalid API key. Please check your configuration.",
        "RateLimitError": "Too many requests. Please wait a moment before trying again.",
        "InvalidRequestError": "Invalid request format. Please try rephrasing.",
        "QuotaExceededError": "API quota exceeded. Please check your usage limits.",
        
        # Model errors
        "ContextLengthError": "Message too long. Try a shorter message.",
        "ModelNotFoundError": "AI model not available. Please check configuration.",
        
        # Tool errors
        "ToolNotFoundError": "The requested tool is not available.",
        "ToolExecutionError": "Tool failed to execute properly.",
        "ServerNotActiveError": "No active servers available.",
        
        # Generic errors
        "ValueError": "Invalid input provided.",
        "KeyError": "Required information missing.",
        "Exception": "An unexpected error occurred."
    }
    
    @classmethod
    def format_error(cls, error: Exception) -> str:
        """Format an exception into a user-friendly message"""
        error_type = type(error).__name__
        
        # Check for specific error messages
        if error_type in cls.ERROR_MESSAGES:
            base_message = cls.ERROR_MESSAGES[error_type]
        else:
            # Check if it's a known error family
            for known_type, message in cls.ERROR_MESSAGES.items():
                if known_type in error_type:
                    base_message = message
                    break
            else:
                base_message = cls.ERROR_MESSAGES["Exception"]
        
        # Add specific error details if available
        error_str = str(error)
        if error_str and error_str != error_type:
            # Don't repeat the error type
            if not error_str.startswith(error_type):
                return f"{base_message}\nDetails: {error_str}"
        
        return base_message
    
    @classmethod
    def format_api_error(cls, status_code: int, message: str = "") -> str:
        """Format API errors based on status code"""
        status_messages = {
            400: "Invalid request. Please check your input.",
            401: "Authentication failed. Please check your API key.",
            403: "Access denied. You don't have permission for this action.",
            404: "Resource not found.",
            429: "Too many requests. Please slow down.",
            500: "Server error. Please try again later.",
            502: "Gateway error. The service is temporarily unavailable.",
            503: "Service unavailable. Please try again later."
        }
        
        base_message = status_messages.get(
            status_code, 
            f"Request failed with status {status_code}"
        )
        
        if message:
            return f"{base_message}\nDetails: {message}"
        return base_message


class StatusDisplay:
    """Displays status information in the chat"""
    
    @staticmethod
    def format_status_line(chat_session) -> str:
        """Format a status line for display"""
        mode = "enhanced" if hasattr(chat_session, 'auto_mode') else "basic"
        servers = len(chat_session.active_servers)
        total_servers = len(chat_session.servers)
        tools = len(chat_session.all_tools)
        
        # Get context info if available
        context_info = ""
        if hasattr(chat_session, 'context_manager'):
            cm = chat_session.context_manager
            tokens = cm.current_tokens
            max_tokens = cm.max_tokens
            context_info = f" | Context: {tokens}/{max_tokens} tokens"
        
        return f"[{mode.upper()} MODE] Servers: {servers}/{total_servers} | Tools: {tools}{context_info}"
    
    @staticmethod
    def show_welcome(chat_session):
        """Show welcome message with status"""
        print("\n🚀 SwarmBot MCP Client")
        print("=" * 60)
        print(StatusDisplay.format_status_line(chat_session))
        print("=" * 60)
        print("\n💬 Type 'help' for commands, 'quit' to exit")
