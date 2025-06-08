"""
Anthropic Claude LLM Client Implementation
High-quality responses using Anthropic's Claude models
"""

import asyncio
from typing import List, Dict, Optional, AsyncGenerator
from anthropic import Anthropic, AsyncAnthropic
import anthropic

from .base_client import BaseLLMClient


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude LLM client implementation."""
    
    DEFAULT_MODEL = "claude-3-haiku-20240307"  # Fast and cost-effective
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model or self.DEFAULT_MODEL)
        self.client = Anthropic(api_key=api_key)
        self.async_client = AsyncAnthropic(api_key=api_key)
        
    def format_messages(self, messages: List[Dict[str, str]]) -> tuple:
        """Format messages for Anthropic's API."""
        system_message = ""
        formatted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message += msg["content"] + "\n"
            else:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return system_message.strip(), formatted_messages
    
    async def complete(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Get a completion from Claude."""
        try:
            system_prompt, formatted_messages = self.format_messages(messages)
            
            # Use default parameters if not provided
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 4096)
            
            response = await self.async_client.messages.create(
                model=self.model,
                system=system_prompt if system_prompt else None,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.content[0].text
            
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {e}")
            if "rate_limit" in str(e).lower():
                return "Rate limit reached. Please wait a moment and try again."
            return self.handle_error(e)
        except Exception as e:
            return self.handle_error(e)
    
    async def stream_complete(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Stream a completion from Claude."""
        try:
            system_prompt, formatted_messages = self.format_messages(messages)
            
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 4096)
            
            async with self.async_client.messages.stream(
                model=self.model,
                system=system_prompt if system_prompt else None,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            yield self.handle_error(e)
    
    def validate_connection(self) -> bool:
        """Validate the Anthropic API key."""
        try:
            # Try a simple completion
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            self.logger.error(f"Anthropic validation failed: {e}")
            return False
