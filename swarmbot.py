#!/usr/bin/env python3
"""
SwarmBot - AI Assistant with MCP Tools
Single entry point for the application
"""

import sys
import warnings
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Suppress asyncio cleanup warnings on Windows
if sys.platform == 'win32':
    warnings.filterwarnings("ignore", category=RuntimeWarning, 
                          message=".*Event loop is closed.*")
    warnings.filterwarnings("ignore", category=ResourceWarning)

from src.core.app import SwarmBotApp


def main():
    """Main entry point for SwarmBot"""
    app = SwarmBotApp()
    return app.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
