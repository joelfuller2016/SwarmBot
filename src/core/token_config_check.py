"""
SwarmBot Token Configuration Test
This module runs on startup to verify the token truncation fix is working
"""

import os
import logging
from src.config import Configuration

logger = logging.getLogger(__name__)


def verify_token_configuration():
    """Verify that token configuration is properly set up"""
    try:
        # Load configuration
        config = Configuration()
        
        # Check if max_context_tokens is available
        if hasattr(config, 'max_context_tokens'):
            current_limit = config.max_context_tokens
            
            # Log the configuration
            logger.info(f"✅ Token configuration loaded successfully")
            logger.info(f"   MAX_CONTEXT_TOKENS = {current_limit}")
            
            # Show improvement over old hardcoded limit
            if current_limit > 4000:
                improvement = current_limit / 4000
                logger.info(f"   Improvement: {improvement:.1f}x over old 4000 token limit")
            
            # Provide recommendations based on limit
            if current_limit < 8000:
                logger.warning("   Consider increasing MAX_CONTEXT_TOKENS for better performance")
            elif current_limit > 100000:
                logger.warning("   Very large context window - monitor memory usage")
            
            return True
        else:
            logger.error("❌ max_context_tokens not found in Configuration")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verifying token configuration: {e}")
        return False


def add_startup_check():
    """Add this check to SwarmBot startup sequence"""
    # This function should be called from app.py during initialization
    success = verify_token_configuration()
    
    if not success:
        logger.warning("Token configuration verification failed - using defaults")
        logger.warning("Add MAX_CONTEXT_TOKENS to your .env file")
    
    return success


# Quick test function for manual verification
def test_token_config():
    """Run this to manually test token configuration"""
    print("\n🔧 SwarmBot Token Configuration Test")
    print("=" * 40)
    
    # Check environment variable
    env_value = os.getenv("MAX_CONTEXT_TOKENS")
    if env_value:
        print(f"✅ Environment variable set: {env_value}")
    else:
        print("❌ MAX_CONTEXT_TOKENS not found in environment")
        print("   Please add to .env file")
        return
    
    # Check configuration loading
    try:
        config = Configuration()
        if hasattr(config, 'max_context_tokens'):
            print(f"✅ Configuration loaded: {config.max_context_tokens} tokens")
            print(f"   Improvement: {config.max_context_tokens / 4000:.1f}x")
        else:
            print("❌ Configuration missing max_context_tokens")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    print("=" * 40)


if __name__ == "__main__":
    # Run manual test
    test_token_config()