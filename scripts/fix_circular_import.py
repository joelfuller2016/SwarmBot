#!/usr/bin/env python3
"""
Fix circular import issue in SwarmBot
Run this from the SwarmBot project root directory
"""

import sys
import re
from pathlib import Path

def fix_core_app():
    """Fix the circular import in src/core/app.py"""
    app_file = Path("src/core/app.py")
    
    if not app_file.exists():
        print(f"Error: {app_file} not found")
        return False
    
    print(f"Reading {app_file}...")
    content = app_file.read_text()
    original_content = content
    
    # Check if already fixed
    if 'from src.chat_session import ChatSession' not in content:
        print("  ✓ ChatSession import already removed from top level")
    else:
        # Remove the import from top
        content = re.sub(r'^from src\.chat_session import ChatSession\n', '', content, flags=re.MULTILINE)
        print("  ✓ Removed ChatSession import from top level")
    
    # Check if lazy import already exists
    if 'from src.chat_session import ChatSession' in content and 'async def run_chat_session' in content:
        print("  ✓ Lazy import already exists in run_chat_session")
    else:
        # Add lazy import in run_chat_session method
        # Find the line after the docstring
        pattern = r'(async def run_chat_session\(self, mode: str, args: argparse\.Namespace\) -> None:\n\s+"""Run the main chat session""")'
        
        def add_import(match):
            return match.group(0) + '\n        from src.chat_session import ChatSession'
        
        new_content = re.sub(pattern, add_import, content)
        if new_content != content:
            content = new_content
            print("  ✓ Added lazy import to run_chat_session method")
    
    # Handle EnhancedChatSession import
    if 'from src.enhanced_chat_session import EnhancedChatSession' in content:
        # Check if it's at the top level
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == 'from src.enhanced_chat_session import EnhancedChatSession':
                # Remove this line
                lines[i] = ''
                print("  ✓ Removed EnhancedChatSession import from top level")
                break
        
        content = '\n'.join(lines)
        
        # Add lazy import where it's used
        pattern = r'(\s+else:\n\s+)(chat_session = EnhancedChatSession)'
        replacement = r'\1from src.enhanced_chat_session import EnhancedChatSession\n\1\2'
        
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            print("  ✓ Added lazy import for EnhancedChatSession")
    
    # Write back if changed
    if content != original_content:
        app_file.write_text(content)
        print("✅ Fixed src/core/app.py")
    else:
        print("✅ src/core/app.py already fixed")
    
    return True

def fix_diagnose_ui():
    """Fix the path issue in scripts/diagnose_ui.py"""
    diag_file = Path("scripts/diagnose_ui.py")
    
    if not diag_file.exists():
        print(f"Error: {diag_file} not found")
        return False
    
    print(f"\nReading {diag_file}...")
    content = diag_file.read_text()
    original_content = content
    
    # Check if already fixed
    if 'project_root = Path(__file__).parent.parent' in content:
        print("✅ scripts/diagnose_ui.py already fixed")
        return True
    
    # Fix the project_root path
    content = content.replace(
        'project_root = Path(__file__).parent',
        'project_root = Path(__file__).parent.parent'
    )
    
    if content != original_content:
        diag_file.write_text(content)
        print("✅ Fixed scripts/diagnose_ui.py")
    else:
        print("❌ Could not fix scripts/diagnose_ui.py - manual fix required")
        return False
    
    return True

def verify_fix():
    """Try to import the modules to verify the fix worked"""
    print("\nVerifying fix...")
    
    try:
        # Add project root to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Try importing the problematic modules
        print("  Testing imports...")
        
        # This should work now
        from src.config import Configuration
        print("  ✓ Configuration import successful")
        
        from src.core.app import SwarmBotApp
        print("  ✓ SwarmBotApp import successful")
        
        # Try importing ChatSession directly
        from src.chat_session import ChatSession
        print("  ✓ ChatSession import successful")
        
        print("\n✅ All imports working correctly!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import still failing: {e}")
        print("   You may need to apply additional fixes manually")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error during verification: {e}")
        return False

def main():
    print("=" * 60)
    print("SwarmBot Circular Import Fix Tool")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src").exists() or not Path("scripts").exists():
        print("\n❌ Error: Must run from SwarmBot project root directory")
        print("   Current directory:", Path.cwd())
        print("   Please cd to the SwarmBot directory and run again")
        return 1
    
    print("\nApplying fixes...")
    
    # Apply both fixes
    success1 = fix_core_app()
    success2 = fix_diagnose_ui()
    
    if success1 and success2:
        print("\n" + "=" * 60)
        print("✅ All fixes applied successfully!")
        print("=" * 60)
        
        # Try to verify
        verify_fix()
        
        print("\nNext steps:")
        print("1. Run: python launch.py")
        print("2. Choose option 4 to validate configuration")
        print("3. Choose option 1, 2, or 3 to start SwarmBot")
        
    else:
        print("\n" + "=" * 60)
        print("❌ Some fixes failed. Please check the output above.")
        print("=" * 60)
        print("\nYou may need to apply the fixes manually.")
        print("See CIRCULAR_IMPORT_FIX.md for manual instructions.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
