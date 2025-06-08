"""
Base LLM Client Interface
Defines the contract for all LLM client implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.logger = logger.getChild(self.__class__.__name__)
        
    @abstractmethod
    async def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Get a completion from the LLM."""
        pass
    
    @abstractmethod
    async def stream_complete(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Stream a completion from the LLM."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate the API key and connection."""
        pass
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for the specific LLM provider."""
        return messages
    
    def handle_error(self, error: Exception) -> str:
        """Handle errors in a consistent way."""
        error_msg = f"LLM Error ({self.__class__.__name__}): {str(error)}"
        self.logger.error(error_msg)
        return "I encountered an error while processing your request. Please try again."
