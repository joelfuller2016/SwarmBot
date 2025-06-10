"""
Conversation context management for SwarmBot
Handles message history, token counting, and context window optimization
"""

import logging
from collections import deque
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

# Simple token estimation (can be replaced with tiktoken)
def estimate_tokens(text: str) -> int:
    """Simple token estimation - ~4 chars per token"""
    return len(text) // 4


@dataclass
class Message:
    """Represents a conversation message"""
    role: str
    content: str
    tokens: int
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Message':
        """Create Message from dictionary"""
        content = data['content']
        return cls(
            role=data['role'],
            content=content,
            tokens=estimate_tokens(content),
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for LLM"""
        return {
            'role': self.role,
            'content': self.content
        }


class ConversationContext:
    """
    Manages conversation context with token-aware windowing.
    Follows SwarmBot's existing patterns.
    """
    
    def __init__(self, 
                 window_size: int = 20,  # Larger default for better context
                 max_tokens: int = 4000,
                 preserve_system: bool = True):
        """Initialize context manager"""
        self.window_size = window_size
        self.max_tokens = max_tokens
        self.preserve_system = preserve_system
        
        # Use deque for efficient sliding window
        self.messages = deque(maxlen=window_size)
        self.system_message: Optional[Message] = None
        self.current_tokens = 0
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the context"""
        message = Message(
            role=role,
            content=content,
            tokens=estimate_tokens(content),
            metadata=metadata or {}
        )
        
        # Handle system messages specially
        if role == 'system' and self.preserve_system:
            self.system_message = message
            logger.debug(f"Updated system message ({message.tokens} tokens)")
        else:
            self.messages.append(message)
            logger.debug(f"Added {role} message ({message.tokens} tokens)")
        
        self._update_token_count()
    
    def get_context_for_llm(self) -> List[Dict[str, str]]:
        """
        Get formatted context for LLM within token limits.
        Returns list of message dictionaries.
        """
        context = []
        token_count = 0
        
        # Always include system message if present
        if self.system_message and self.preserve_system:
            context.append(self.system_message.to_dict())
            token_count += self.system_message.tokens
        
        # Add messages from newest to oldest (then reverse)
        temp_messages = []
        for message in reversed(self.messages):
            if token_count + message.tokens > self.max_tokens:
                logger.info(f"Truncating context at {token_count} tokens")
                break
            temp_messages.append(message)
            token_count += message.tokens
        
        # Reverse to maintain chronological order
        temp_messages.reverse()
        
        # Convert to dict format
        for msg in temp_messages:
            context.append(msg.to_dict())
        
        logger.debug(f"Returning context with {len(context)} messages, {token_count} tokens")
        return context
    
    def _update_token_count(self):
        """Update current token count"""
        self.current_tokens = sum(msg.tokens for msg in self.messages)
        if self.system_message:
            self.current_tokens += self.system_message.tokens
    
    def clear(self, keep_system: bool = True):
        """Clear conversation history"""
        self.messages.clear()
        if not keep_system:
            self.system_message = None
        self._update_token_count()
        logger.info("Conversation context cleared")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get context summary for status display"""
        return {
            'message_count': len(self.messages),
            'current_tokens': self.current_tokens,
            'max_tokens': self.max_tokens,
            'window_size': self.window_size,
            'has_system_message': self.system_message is not None
        }
    
    def export_history(self) -> List[Dict[str, Any]]:
        """Export full conversation history"""
        history = []
        if self.system_message:
            history.append(self.system_message.to_dict())
        history.extend([msg.to_dict() for msg in self.messages])
        return history
