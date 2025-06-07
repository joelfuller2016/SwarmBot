"""
LLM Client module for SwarmBot
Manages communication with various LLM providers
"""

import logging
from typing import List, Dict
from enum import Enum

import requests

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    AZURE = "azure"


class LLMClient:
    """Manages communication with various LLM providers."""

    def __init__(self, provider: str, api_key: str) -> None:
        self.provider: str = provider
        self.api_key: str = api_key
        self.endpoints = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "groq": "https://api.groq.com/openai/v1/chat/completions",
            "azure": "https://models.inference.ai.azure.com/chat/completions"
        }
        self.models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-opus-20240229",
            "groq": "mixtral-8x7b-32768",
            "azure": "gpt-4o-mini"
        }

    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Get a response from the configured LLM provider."""
        try:
            if self.provider == "anthropic":
                return self._get_anthropic_response(messages)
            else:
                return self._get_openai_compatible_response(messages)
        except requests.exceptions.RequestException as e:
            error_msg = f"Error getting LLM response: {str(e)}"
            logger.error(error_msg)
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return f"I encountered an error while processing your request. Please try again."

    def _get_openai_compatible_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from OpenAI-compatible endpoints."""
        url = self.endpoints[self.provider]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "messages": messages,
            "model": self.models[self.provider],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    def _get_anthropic_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from Anthropic Claude API."""
        url = self.endpoints[self.provider]
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages format for Anthropic
        system_message = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message += msg["content"] + "\n"
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": self.models[self.provider],
            "messages": anthropic_messages,
            "system": system_message.strip(),
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['content'][0]['text']