"""
Logging utilities for SwarmBot
Handles custom logging filters and configuration
"""

import logging
import re


class MCPNotificationFilter(logging.Filter):
    """Filter out non-critical MCP notification validation warnings."""
    
    def filter(self, record):
        # Filter out MCP notification validation warnings
        if record.levelname == "WARNING" and "Failed to validate notification" in record.getMessage():
            return False
        
        # Filter out specific MCP stderr notifications
        if "notifications/stderr" in record.getMessage():
            return False
            
        return True


class CleanConsoleFormatter(logging.Formatter):
    """Custom formatter that cleans up console output."""
    
    def format(self, record):
        # Skip timestamp for console output if it's from chat session
        if hasattr(record, 'name') and 'chat_session' in record.name:
            return record.getMessage()
        return super().format(record)


def configure_logging(log_file='swarmbot.log', console_level=logging.INFO):
    """Configure logging with custom filters and formatters."""
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = CleanConsoleFormatter(
        '%(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(console_level)
    
    # Add MCP notification filter to both handlers
    mcp_filter = MCPNotificationFilter()
    file_handler.addFilter(mcp_filter)
    console_handler.addFilter(mcp_filter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels to reduce noise
    logging.getLogger('mcp').setLevel(logging.ERROR)
    logging.getLogger('pydantic').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)
