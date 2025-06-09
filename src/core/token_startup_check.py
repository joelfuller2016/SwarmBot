"""
Token Configuration Startup Check
"""

import os
import logging
from src.config import Configuration

logger = logging.getLogger(__name__)


def verify_token_configuration():
    """Verify token configuration on startup"""
    try:
        config = Configuration()
        
        if hasattr(config, 'max_context_tokens'):
            limit = config.max_context_tokens
            logger.info(f"✅ Token limit configured: {limit} (was 4000)")
            return True
        else:
            logger.error("❌ max_context_tokens not configured")
            return False
    except Exception as e:
        logger.error(f"❌ Token config error: {e}")
        return False


def add_startup_check():
    """Add to SwarmBot startup"""
    if not verify_token_configuration():
        logger.warning("Add MAX_CONTEXT_TOKENS to .env file")