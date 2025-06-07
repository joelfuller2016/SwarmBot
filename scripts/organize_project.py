#!/usr/bin/env python3
"""
Organize SwarmBot project files
Moves documentation to Docs folder and organizes project structure
"""

import os
import shutil
from pathlib import Path

def organize_project():
    project_root = Path(r"C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot")
    docs_folder = project_root / "Docs"
    scripts_folder = project_root / "scripts"
    
    # Documentation files to move
    doc_files = [
        "IMPLEMENTATION_SUMMARY.md",
        "PRIORITY_FEATURES_INTEGRATION_GUIDE.md",
        "PRIORITY_TASKS_IMPLEMENTATION_SUMMARY.md",
        "PROJECT_REVIEW_SUMMARY.md",
        "REORGANIZATION_SUMMARY.md",
        "SWARM_ARCHITECTURE.md",
        "TASK_ORGANIZATION_SUMMARY.md",
        "WORKFLOW_DIAGRAM.md",
        "env_auto_prompt_additions.txt"
    ]
    
    # Test files to move to tests folder
    test_files = [
        "test_quick.py",
        "test_structure.py"
    ]
    
    # Script files to move
    script_files = [
        "swarmbot_fixed.py"  # This is the fixed version, should be in scripts
    ]
    
    # Move documentation files
    for doc_file in doc_files:
        source = project_root / doc_file
        if source.exists():
            dest = docs_folder / doc_file
            print(f"Moving {doc_file} to Docs folder...")
            shutil.move(str(source), str(dest))
    
    # Move test files
    tests_folder = project_root / "tests"
    for test_file in test_files:
        source = project_root / test_file
        if source.exists():
            dest = tests_folder / test_file
            print(f"Moving {test_file} to tests folder...")
            shutil.move(str(source), str(dest))
    
    # Move script files
    for script_file in script_files:
        source = project_root / script_file
        if source.exists():
            dest = scripts_folder / script_file
            print(f"Moving {script_file} to scripts folder...")
            shutil.move(str(source), str(dest))
    
    print("\nProject organization complete!")
    print("\nRemaining files in root (should stay):")
    print("- README.MD")
    print("- requirements.txt")
    print("- swarmbot.py (main launcher)")
    print("- swarmbot.bat/.ps1/.sh (platform launchers)")
    print("- .env.example")
    print("- .gitignore")
    print("- .roomodes")
    print("- .windsurfrules")

if __name__ == "__main__":
    organize_project()