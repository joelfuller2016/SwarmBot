"""
LLM Client module for SwarmBot
Manages communication with various LLM providers

This module now uses the new LLM client factory for improved reliability
and proper SDK usage, while maintaining backward compatibility.
"""

import logging
from typing import List, Dict
from enum import Enum

# Import the new adapter
from .llm_client_adapter import LLMClient as LLMClientAdapter

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    AZURE = "azure"


# For backward compatibility, inherit from the adapter
class LLMClient(LLMClientAdapter):
    """
    LLM Client that maintains backward compatibility while using
    the new implementation underneath.
    
    The old interface is preserved but now uses proper SDK implementations
    instead of raw HTTP requests.
    """
    pass
