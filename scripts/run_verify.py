import os
import sys

# Change to the SwarmBot directory
os.chdir(r'C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot')

# Run the verification script
exec(open('tests/verify_websocket_fixes.py').read())
