"""
LLM Client Factory
Creates and manages LLM client instances with fallback support
"""

import os
import logging
from typing import Optional, List, Dict
from enum import Enum

from .base_client import BaseLLMClient
from .groq_client import GroqClient
from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    GROQ = "groq"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class LLMClientFactory:
    """Factory for creating LLM clients with fallback support."""
    
    # Provider priority order (fastest/most reliable first)
    PROVIDER_PRIORITY = [
        LLMProvider.GROQ,
        LLMProvider.ANTHROPIC,
        LLMProvider.OPENAI
    ]
    
    # Map providers to their client classes
    PROVIDER_CLIENTS = {
        LLMProvider.GROQ: GroqClient,
        LLMProvider.ANTHROPIC: AnthropicClient,
        LLMProvider.OPENAI: OpenAIClient
    }
    
    # Map providers to their environment variable names
    PROVIDER_ENV_VARS = {
        LLMProvider.GROQ: "GROQ_API_KEY",
        LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
        LLMProvider.OPENAI: "OPENAI_API_KEY"
    }
    
    @classmethod
    def create_client(cls, provider: str = None, api_key: str = None, model: str = None) -> Optional[BaseLLMClient]:
        """
        Create an LLM client for the specified provider.
        
        Args:
            provider: Provider name (groq, anthropic, openai). If None, tries all.
            api_key: API key for the provider. If None, reads from environment.
            model: Model to use. If None, uses provider default.
            
        Returns:
            LLM client instance or None if creation failed.
        """
        if provider:
            # Try specific provider
            try:
                provider_enum = LLMProvider(provider.lower())
                return cls._create_single_client(provider_enum, api_key, model)
            except ValueError:
                logger.error(f"Unknown provider: {provider}")
                return None
        else:
            # Try all providers in priority order
            return cls.create_client_with_fallback(model=model)
    
    @classmethod
    def _create_single_client(cls, provider: LLMProvider, api_key: str = None, model: str = None) -> Optional[BaseLLMClient]:
        """Create a single LLM client."""
        # Get API key
        if not api_key:
            env_var = cls.PROVIDER_ENV_VARS.get(provider)
            api_key = os.getenv(env_var)
            
        if not api_key:
            logger.warning(f"No API key found for {provider.value}")
            return None
        
        # Get client class
        client_class = cls.PROVIDER_CLIENTS.get(provider)
        if not client_class:
            logger.error(f"No client implementation for {provider.value}")
            return None
        
        try:
            # Create client
            client = client_class(api_key, model)
            
            # Validate connection
            if client.validate_connection():
                logger.info(f"Successfully created {provider.value} client")
                return client
            else:
                logger.warning(f"Failed to validate {provider.value} client")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create {provider.value} client: {e}")
            return None
    
    @classmethod
    def create_client_with_fallback(cls, preferred_provider: str = None, model: str = None) -> Optional[BaseLLMClient]:
        """
        Create an LLM client with automatic fallback.
        
        Args:
            preferred_provider: Preferred provider to try first.
            model: Model to use.
            
        Returns:
            First working LLM client or None if all fail.
        """
        # Build provider order
        providers = []
        
        if preferred_provider:
            try:
                preferred = LLMProvider(preferred_provider.lower())
                providers.append(preferred)
            except ValueError:
                logger.warning(f"Invalid preferred provider: {preferred_provider}")
        
        # Add remaining providers in priority order
        for provider in cls.PROVIDER_PRIORITY:
            if provider not in providers:
                providers.append(provider)
        
        # Try each provider
        for provider in providers:
            client = cls._create_single_client(provider, model=model)
            if client:
                return client
        
        logger.error("Failed to create any LLM client")
        return None
    
    @classmethod
    def test_all_providers(cls) -> Dict[str, bool]:
        """
        Test all configured providers.
        
        Returns:
            Dictionary mapping provider names to success status.
        """
        results = {}
        
        for provider in cls.PROVIDER_PRIORITY:
            client = cls._create_single_client(provider)
            results[provider.value] = client is not None
            
        return results
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of providers with configured API keys."""
        available = []
        
        for provider, env_var in cls.PROVIDER_ENV_VARS.items():
            if os.getenv(env_var):
                available.append(provider.value)
        
        return available
