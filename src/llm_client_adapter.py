"""
LLM Client Adapter
Adapts the new async LLM clients to work with existing synchronous code
"""

import asyncio
import logging
from typing import List, Dict, Optional

from .llm.client_factory import LLMClientFactory
from .llm.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Adapter class that maintains backward compatibility with existing code
    while using the new LLM client factory underneath.
    """

    def __init__(self, provider: str = None, api_key: str = None) -> None:
        """Initialize LLM client with automatic fallback."""
        self.provider = provider
        self.api_key = api_key
        
        # Create the underlying async client
        self._client: Optional[BaseLLMClient] = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize the underlying client."""
        if self.provider and self.api_key:
            # Use specific provider
            self._client = LLMClientFactory.create_client(
                provider=self.provider,
                api_key=self.api_key
            )
        else:
            # Use fallback mechanism
            self._client = LLMClientFactory.create_client_with_fallback(
                preferred_provider=self.provider
            )
        
        if not self._client:
            raise ValueError("Failed to initialize any LLM provider")
    
    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Get a response from the LLM (synchronous interface).
        
        This method maintains backward compatibility with existing code.
        """
        if not self._client:
            return "LLM client not initialized. Please check your API keys."
        
        try:
            # Check if there's already an event loop running
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, use run_coroutine_threadsafe
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(
                    self._client.complete(messages), loop
                )
                return future.result(timeout=30)
            except RuntimeError:
                # No event loop running, create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    response = loop.run_until_complete(
                        self._client.complete(messages)
                    )
                    return response
                finally:
                    loop.close()
                    
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            return self._client.handle_error(e) if self._client else str(e)
    
    async def get_response_async(self, messages: List[Dict[str, str]]) -> str:
        """Get a response from the LLM (async interface)."""
        if not self._client:
            return "LLM client not initialized. Please check your API keys."
        
        return await self._client.complete(messages)
    
    def validate_connection(self) -> bool:
        """Validate the LLM connection."""
        return self._client.validate_connection() if self._client else False
    
    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._client is not None
    
    @property
    def provider_name(self) -> str:
        """Get the name of the active provider."""
        if self._client:
            return self._client.__class__.__name__.replace("Client", "")
        return "None"
