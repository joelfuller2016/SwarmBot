#!/usr/bin/env python3
"""
Fix UI launch errors by copying fixed files
"""

import shutil
import os

# Fix 1: Copy fixed agent_manager.py
print("Fixing agent_manager.py...")
src = r'C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot\src\agents\agent_manager_fixed.py'
dst = r'C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot\src\agents\agent_manager.py'

if os.path.exists(src):
    shutil.copy2(src, dst)
    print("✓ Fixed agent_manager.py")
    os.remove(src)  # Clean up
else:
    print("✗ Could not find agent_manager_fixed.py")

# Fix 2: Fix app.py config issue
print("\nFixing app.py...")
app_path = r'C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot\src\ui\dash\app.py'

with open(app_path, 'r') as f:
    content = f.read()

# Replace the problematic config.update
content = content.replace(
    '''    # Configure app
    app.config.update({
        "app_name": "SwarmBot",
        "update_interval": 1000,  # 1 second update interval
        "max_agents": 50,
        "max_tasks_display": 100,
        "theme": "dark"
    })''',
    '''    # Store custom configuration as app attributes
    app.app_name = "SwarmBot"
    app.update_interval = 1000  # 1 second update interval
    app.max_agents = 50
    app.max_tasks_display = 100
    app.theme = "dark"'''
)

with open(app_path, 'w') as f:
    f.write(content)

print("✓ Fixed app.py")

# Clean up fix scripts
for script in ['fix_agent_type.py', 'fix_ui_errors.py']:
    path = os.path.join(r'C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot', script)
    if os.path.exists(path):
        os.remove(path)
        print(f"✓ Cleaned up {script}")

print("\n✅ All fixes applied! Try running 'python swarmbot.py --ui' again.")
