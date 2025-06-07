#!/usr/bin/env python3
"""
Launch script for SwarmBot Dashboard
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ui.dash.integration import main

if __name__ == "__main__":
    main()
