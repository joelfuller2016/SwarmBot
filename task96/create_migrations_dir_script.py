#!/usr/bin/env python3
"""
Create migrations directory structure for SwarmBot cost tracking
"""

import os
from pathlib import Path


def create_migrations_structure(project_root):
    """Create the migrations directory structure"""
    
    # Define directories to create
    directories = [
        "migrations",
        "src/database",
        "tests/database"
    ]
    
    # Create directories
    for directory in directories:
        dir_path = Path(project_root) / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create __init__.py files for Python packages
    init_files = [
        "src/database/__init__.py",
        "tests/database/__init__.py"
    ]
    
    for init_file in init_files:
        file_path = Path(project_root) / init_file
        if not file_path.exists():
            file_path.write_text("")
            print(f"Created file: {file_path}")
    
    # Create a migration log JSON file
    migration_log = Path(project_root) / "migrations" / "migration_log.json"
    if not migration_log.exists():
        migration_log.write_text('{"migrations": [], "version": "1.0.0"}')
        print(f"Created file: {migration_log}")
    
    print("\nMigration directory structure created successfully!")


if __name__ == "__main__":
    # Get the project root from the current working directory
    project_root = os.getcwd()
    
    # Confirm this is the SwarmBot project
    if not os.path.exists(os.path.join(project_root, "swarmbot.py")):
        print("Error: This doesn't appear to be the SwarmBot project root.")
        print("Please run this script from the SwarmBot project directory.")
        exit(1)
    
    create_migrations_structure(project_root)