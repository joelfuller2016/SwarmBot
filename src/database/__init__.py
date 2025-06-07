"""
Database module for SwarmBot
Handles persistent storage of chat history and raw data
"""

from .chat_storage import ChatDatabase, ChatLogger

__all__ = ['ChatDatabase', 'ChatLogger']
