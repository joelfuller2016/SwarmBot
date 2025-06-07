"""
Configuration module for SwarmBot
Handles environment variables and configuration loading
"""

import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Configuration:
    """Manages configuration and environment variables for the MCP client."""

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.load_env()
        self._validate_environment()
        
        # Configure LLM provider
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "groq": os.getenv("GROQ_API_KEY"),
            "azure": os.getenv("AZURE_API_KEY")
        }
        
        # Server-specific API keys
        self.server_api_keys = {
            "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
            "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY"),
            "N8N_HOST": os.getenv("N8N_HOST"),
            "N8N_API_KEY": os.getenv("N8N_API_KEY"),
            "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
            "EXA_API_KEY": os.getenv("EXA_API_KEY"),
            "GITHUB_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY")
        }

        # Auto-prompt configuration
        self.auto_prompt_enabled = os.getenv("AUTO_PROMPT_ENABLED", "false").lower() == "true"
        self.auto_prompt_max_iterations = int(os.getenv("AUTO_PROMPT_MAX_ITERATIONS", "1"))
        self.auto_prompt_goal_detection = os.getenv("AUTO_PROMPT_GOAL_DETECTION", "true").lower() == "true"
        self.auto_prompt_save_state = os.getenv("AUTO_PROMPT_SAVE_STATE", "true").lower() == "true"

    @staticmethod
    def load_env() -> None:
        """Load environment variables from .env file."""
        env_path = ".env"
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {env_path}")
        else:
            logger.warning(f"No .env file found at {env_path}")

    def _validate_environment(self) -> None:
        """Validate that required environment variables are set."""
        required_vars = []
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"Missing optional environment variables: {', '.join(missing_vars)}")

    @staticmethod
    def load_config(file_path: str) -> Dict[str, Any]:
        """Load server configuration from JSON file."""
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {file_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise

    @property
    def llm_api_key(self) -> str:
        """Get the LLM API key for the selected provider."""
        key = self.api_keys.get(self.llm_provider)
        if not key:
            raise ValueError(f"API key not found for provider: {self.llm_provider}")
        return key

    def get_server_env(self, server_config: Dict[str, Any]) -> Dict[str, str]:
        """Get environment variables for a specific server."""
        env = os.environ.copy()
        
        # Add server-specific environment variables from config
        if 'env' in server_config:
            env.update(server_config['env'])
        
        # Add API keys from .env file
        for key, value in self.server_api_keys.items():
            if value:
                env[key] = value
        
        return env