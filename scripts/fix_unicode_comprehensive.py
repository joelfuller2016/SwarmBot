#!/usr/bin/env python3
"""
Comprehensive Unicode/Emoji Fix for SwarmBot Project
Fixes all emoji characters in Python files
"""

import os
import re
from pathlib import Path
import sys


# Comprehensive emoji to ASCII replacements
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
    '🚀': '[START]',
    '🎉': '[SUCCESS]',
    '📊': '[STATS]',
    '🧪': '[TEST]',
    '📈': '[CHART]',
    '📉': '[DECLINE]',
    '🔧': '[TOOL]',
    '🛠️': '[BUILD]',
    '📝': '[NOTE]',
    '📂': '[FOLDER]',
    '📁': '[DIRECTORY]',
    '💡': '[IDEA]',
    '🐛': '[BUG]',
    '🔥': '[HOT]',
    '⭐': '[STAR]',
    '👍': '[GOOD]',
    '👎': '[BAD]',
    '💻': '[COMPUTER]',
    '🌐': '[WEB]',
    '🔄': '[REFRESH]',
    '⏰': '[TIME]',
    '📅': '[DATE]',
    '🎯': '[TARGET]',
    '🏃': '[RUN]',
    '🛑': '[STOP]',
    '⏸️': '[PAUSE]',
    '▶️': '[PLAY]',
    '◀️': '[BACK]',
    '⏭️': '[NEXT]',
    '⏮️': '[PREV]',
    '🔴': '[RED]',
    '🟢': '[GREEN]',
    '🟡': '[YELLOW]',
    '🔵': '[BLUE]',
    '⚫': '[BLACK]',
    '🟣': '[PURPLE]',
    '🟠': '[ORANGE]',
    '🟤': '[BROWN]'
}


def fix_file(file_path: Path) -> bool:
    """Fix emoji characters in a single file"""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check if file needs fixing
        original_content = content
        
        # Replace all emojis
        for emoji, replacement in REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # Also check for any remaining unicode emoji ranges
        # This regex catches most emoji characters
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U00002600-\U000027BF"  # Miscellaneous symbols
            "\U00002B50-\U00002B55"  # Stars
            "]+", 
            flags=re.UNICODE
        )
        
        # Replace any remaining emojis with [EMOJI]
        content = emoji_pattern.sub('[EMOJI]', content)
        
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


def scan_file(file_path: Path) -> list:
    """Scan file for remaining emoji characters"""
    emojis_found = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Find all emoji characters
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U00002600-\U000027BF"
            "\U00002B50-\U00002B55"
            "]+", 
            flags=re.UNICODE
        )
        
        matches = emoji_pattern.findall(content)
        if matches:
            emojis_found.extend(matches)
            
        # Also check for known emojis
        for emoji in REPLACEMENTS.keys():
            if emoji in content:
                emojis_found.append(emoji)
                
    except Exception as e:
        print(f"[ERROR] Failed to scan {file_path}: {e}")
        
    return emojis_found


def main():
    """Fix all Python files in the project"""
    # Get the script directory and project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    print("[SwarmBot] Comprehensive Unicode/Emoji Fix")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print()
    
    # First, scan for all emojis
    print("[SCANNING] Looking for emoji characters...")
    all_emojis = set()
    python_files = list(project_root.rglob('*.py'))
    
    for file_path in python_files:
        if '__pycache__' in str(file_path):
            continue
            
        emojis = scan_file(file_path)
        if emojis:
            all_emojis.update(emojis)
            print(f"  Found in {file_path.relative_to(project_root)}: {', '.join(set(emojis))}")
    
    if not all_emojis:
        print("\n[OK] No emoji characters found!")
        return 0
        
    print(f"\n[FOUND] Total unique emojis: {len(all_emojis)}")
    print(f"Emojis: {', '.join(sorted(all_emojis))}")
    
    # Now fix all files
    print("\n[FIXING] Replacing emoji characters...")
    fixed_count = 0
    
    for file_path in python_files:
        if '__pycache__' in str(file_path):
            continue
            
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n[DONE] Fixed {fixed_count} files")
    
    # Verify fix
    print("\n[VERIFYING] Checking for remaining emojis...")
    remaining_files = []
    
    for file_path in python_files:
        if '__pycache__' in str(file_path):
            continue
            
        emojis = scan_file(file_path)
        if emojis:
            remaining_files.append((file_path, emojis))
    
    if remaining_files:
        print(f"\n[WARNING] {len(remaining_files)} files still contain emojis:")
        for file_path, emojis in remaining_files:
            print(f"  {file_path.relative_to(project_root)}: {', '.join(set(emojis))}")
    else:
        print("\n[SUCCESS] All emoji characters have been replaced!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
