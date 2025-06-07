#!/usr/bin/env python3
"""
Legacy launcher - redirects to new unified launcher
"""

import sys
import os

print("ℹ️  This launcher is deprecated. Using swarmbot.py instead...")
print()

# Pass all arguments to the new launcher
os.execvp(sys.executable, [sys.executable, 'swarmbot.py'] + sys.argv[1:])
