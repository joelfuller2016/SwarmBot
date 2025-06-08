"""
Groq LLM Client Implementation
Fast and reliable LLM provider using Groq's API
"""

import asyncio
from typing import List, Dict, Optional, AsyncGenerator
from groq import Groq, AsyncGroq
import groq

from .base_client import BaseLLMClient


class GroqClient(BaseLLMClient):
    """Groq LLM client implementation."""
    
    DEFAULT_MODEL = "mixtral-8x7b-32768"
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self.client = Groq(api_key=api_key)
        self.async_client = AsyncGroq(api_key=api_key)
        
    async def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Get a completion from Groq."""
        try:
            # Use default parameters if not provided
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 4096)
            
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except groq.APIError as e:
            self.logger.error(f"Groq API error: {e}")
            if "rate_limit" in str(e).lower():
                return "Rate limit reached. Please wait a moment and try again."
            return self.handle_error(e)
        except Exception as e:
            return self.handle_error(e)
    
    async def stream_complete(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Stream a completion from Groq."""
        try:
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 4096)
            
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield self.handle_error(e)
    
    def validate_connection(self) -> bool:
        """Validate the Groq API key."""
        try:
            # Try a simple completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            self.logger.error(f"Groq validation failed: {e}")
            return False
