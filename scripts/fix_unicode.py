#!/usr/bin/env python3
"""
Fix Unicode/Emoji Issues in SwarmBot Project
Replaces all emoji characters with ASCII alternatives
"""

import os
import re
from pathlib import Path


# Emoji to ASCII replacements
REPLACEMENTS = {
    '✅': '[OK]',
    '❌': '[ERROR]',
    '⚠️': '[WARNING]',
    '🤖': '[BOT]',
    '💬': '[CHAT]',
    '🚨': '[ALERT]',
    '✨': '[NEW]',
    '🔍': '[SEARCH]',
    '⚙️': '[CONFIG]',
    '⚪': '[*]',
    '❓': '[?]',
    '🚀': '[START]'
}


def fix_file(file_path: Path) -> bool:
    """Fix emoji characters in a single file"""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file needs fixing
        original_content = content
        
        # Replace all emojis
        for emoji, replacement in REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # If content changed, write it back
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[FIXED] {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed to fix {file_path}: {e}")
        return False


def main():
    """Fix all Python files in the project"""
    print("[SwarmBot] Fixing Unicode/Emoji Issues")
    print("=" * 60)
    
    # Get all Python files
    project_root = Path('.')
    python_files = list(project_root.rglob('*.py'))
    
    # Exclude deprecated and test files
    python_files = [
        f for f in python_files 
        if 'deprecated' not in str(f) and '__pycache__' not in str(f)
    ]
    
    fixed_count = 0
    
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n[DONE] Fixed {fixed_count} files")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
