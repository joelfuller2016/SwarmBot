"""
LLM Client Adapter
Adapts the new async LLM clients to work with existing synchronous code
"""

import asyncio
import logging
import traceback
import concurrent.futures
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from .llm.client_factory import LLMClientFactory
from .llm.base_client import BaseLLMClient
from .config import Configuration
from .core.integrated_analyzer import IntegratedAnalyzer

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
        
        # Load configuration
        self.config = Configuration()
        self.timeout = self.config.llm_timeout
        
        # Initialize cost tracking if enabled
        self.cost_tracking_enabled = self.config.get('TRACK_COSTS', True)
        self.integrated_analyzer = None
        self.default_conversation_id = str(uuid.uuid4())
        
        if self.cost_tracking_enabled:
            try:
                self.integrated_analyzer = IntegratedAnalyzer(self.config)
                logger.info("Cost tracking initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize cost tracking: {e}")
                self.cost_tracking_enabled = False
        
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
    
    def _extract_provider_name(self) -> str:
        """Extract the actual provider name from the client class."""
        if self._client:
            class_name = self._client.__class__.__name__
            # Map client class names to provider names
            provider_map = {
                'OpenAIClient': 'openai',
                'AnthropicClient': 'anthropic',
                'GroqClient': 'groq',
                'GoogleClient': 'google',
                'GoogleGeminiClient': 'google',
                'GeminiClient': 'google'
            }
            return provider_map.get(class_name, self.provider or 'unknown')
        return self.provider or 'unknown'
    
    def _track_cost(self, messages: List[Dict[str, str]], response: str, 
                   conversation_id: Optional[str] = None):
        """Track the cost of an LLM request."""
        if not self.cost_tracking_enabled or not self.integrated_analyzer:
            return
        
        try:
            # Extract input text from messages
            input_text = "\n".join([msg.get('content', '') for msg in messages])
            
            # Use provided conversation_id or default
            conv_id = conversation_id or self.default_conversation_id
            
            # Get the actual provider name
            provider = self._extract_provider_name()
            
            # Analyze the request for cost tracking
            self.integrated_analyzer.analyze_request(
                conversation_id=conv_id,
                model=self._client.model if hasattr(self._client, 'model') else 'unknown',
                input_text=input_text,
                output_text=response,
                provider=provider
            )
            
        except Exception as e:
            # Log error but don't break LLM functionality
            logger.error(f"Error tracking cost: {e}")
    
    def get_response(self, messages: List[Dict[str, str]], 
                    conversation_id: Optional[str] = None) -> str:
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
                future = asyncio.run_coroutine_threadsafe(
                    self._client.complete(messages), loop
                )
                response = future.result(timeout=self.timeout)
            except RuntimeError:
                # No event loop running, create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    response = loop.run_until_complete(
                        self._client.complete(messages)
                    )
                finally:
                    loop.close()
            
            # Track cost if successful
            self._track_cost(messages, response, conversation_id)
            
            return response
                    
        except concurrent.futures.TimeoutError as e:
            error_details = {
                "timestamp": datetime.now().isoformat(),
                "error_type": "TimeoutError",
                "error_message": f"LLM request timed out after {self.timeout} seconds",
                "provider": self.provider_name,
                "messages_count": len(messages),
                "first_message_role": messages[0].get('role', 'unknown') if messages else 'no_messages',
                "traceback": traceback.format_exc()
            }
            logger.error(f"LLM Timeout Error: {error_details}")
            return f"Error: LLM request timed out after {self.timeout} seconds. Provider: {self.provider_name}. Try increasing LLM_TIMEOUT environment variable."
        
        except asyncio.TimeoutError as e:
            error_details = {
                "timestamp": datetime.now().isoformat(),
                "error_type": "AsyncioTimeoutError",
                "error_message": str(e) or "Async operation timed out",
                "provider": self.provider_name,
                "messages_count": len(messages),
                "first_message_role": messages[0].get('role', 'unknown') if messages else 'no_messages',
                "traceback": traceback.format_exc()
            }
            logger.error(f"AsyncIO Timeout Error: {error_details}")
            return f"Error: Async operation timed out. Provider: {self.provider_name}. Check network connection and API status."
        
        except Exception as e:
            error_details = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(e).__name__,
                "error_message": str(e),
                "provider": self.provider_name,
                "messages_count": len(messages),
                "first_message_role": messages[0].get('role', 'unknown') if messages else 'no_messages',
                "traceback": traceback.format_exc(),
                "exception_args": getattr(e, 'args', None),
                "exception_attrs": {k: str(v) for k, v in vars(e).items() if not k.startswith('_')} if hasattr(e, '__dict__') else {}
            }
            logger.error(f"Unexpected LLM Error: {error_details}")
            
            # Still try to use the client's error handler if available
            if self._client and hasattr(self._client, 'handle_error'):
                handled_response = self._client.handle_error(e)
                logger.info(f"Client handled error response: {handled_response}")
                return handled_response
            
            # Provide more actionable error messages based on error type
            if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                return f"Error: API key issue for {self.provider_name}. Please check your {self.provider_name.upper()}_API_KEY environment variable."
            elif "rate limit" in str(e).lower():
                return f"Error: Rate limit exceeded for {self.provider_name}. Please wait a moment and try again."
            elif "connection" in str(e).lower() or "network" in str(e).lower():
                return f"Error: Network connection issue with {self.provider_name}. Please check your internet connection."
            
            return f"Error ({type(e).__name__}): {str(e)} - Provider: {self.provider_name}. Check logs for full details."
    
    async def get_response_async(self, messages: List[Dict[str, str]], 
                                conversation_id: Optional[str] = None) -> str:
        """Get a response from the LLM (async interface)."""
        if not self._client:
            return "LLM client not initialized. Please check your API keys."
        
        try:
            response = await self._client.complete(messages)
            
            # Track cost if successful
            self._track_cost(messages, response, conversation_id)
            
            return response
            
        except asyncio.TimeoutError as e:
            error_details = {
                "timestamp": datetime.now().isoformat(),
                "error_type": "AsyncioTimeoutError",
                "error_message": str(e) or "Async operation timed out",
                "provider": self.provider_name,
                "messages_count": len(messages),
                "first_message_role": messages[0].get('role', 'unknown') if messages else 'no_messages',
                "traceback": traceback.format_exc()
            }
            logger.error(f"Async LLM Timeout Error: {error_details}")
            return f"Error: Async operation timed out. Provider: {self.provider_name}. Check network connection and API status."
        except Exception as e:
            error_details = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(e).__name__,
                "error_message": str(e),
                "provider": self.provider_name,
                "messages_count": len(messages),
                "first_message_role": messages[0].get('role', 'unknown') if messages else 'no_messages',
                "traceback": traceback.format_exc(),
                "exception_args": getattr(e, 'args', None)
            }
            logger.error(f"Async LLM Error: {error_details}")
            
            # Still try to use the client's error handler if available
            if self._client and hasattr(self._client, 'handle_error'):
                handled_response = self._client.handle_error(e)
                logger.info(f"Client handled async error response: {handled_response}")
                return handled_response
            
            # Provide more actionable error messages based on error type
            if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                return f"Error: API key issue for {self.provider_name}. Please check your {self.provider_name.upper()}_API_KEY environment variable."
            elif "rate limit" in str(e).lower():
                return f"Error: Rate limit exceeded for {self.provider_name}. Please wait a moment and try again."
            elif "connection" in str(e).lower() or "network" in str(e).lower():
                return f"Error: Network connection issue with {self.provider_name}. Please check your internet connection."
            
            return f"Error ({type(e).__name__}): {str(e)} - Provider: {self.provider_name}. Check logs for full details."
    
    def validate_connection(self) -> bool:
        """Validate the LLM connection."""
        return self._client.validate_connection() if self._client else False
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary if enabled."""
        if self.cost_tracking_enabled and self.integrated_analyzer:
            return self.integrated_analyzer.get_integrated_summary()
        return {"error": "Cost tracking not enabled"}
    
    def shutdown(self):
        """Cleanup and shutdown cost tracking."""
        if self.cost_tracking_enabled and self.integrated_analyzer:
            self.integrated_analyzer.shutdown()
    
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
