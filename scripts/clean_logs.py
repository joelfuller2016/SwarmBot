#!/usr/bin/env python3
"""Script to clean log files while preserving directory structure."""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Define the base directory
BASE_DIR = Path(r"C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot")
LOGS_DIR = BASE_DIR / "logs"

def clean_logs(archive=True):
    """Clean log files, optionally archiving them first."""
    if not LOGS_DIR.exists():
        print("Logs directory not found.")
        return
    
    log_files = list(LOGS_DIR.glob("*.log"))
    
    if not log_files:
        print("No log files found.")
        return
    
    if archive:
        # Create archive directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = LOGS_DIR / f"archive_{timestamp}"
        archive_dir.mkdir(exist_ok=True)
        
        # Move logs to archive
        for log_file in log_files:
            archive_path = archive_dir / log_file.name
            shutil.move(str(log_file), str(archive_path))
            print(f"Archived: {log_file.name}")
    else:
        # Delete logs directly
        for log_file in log_files:
            log_file.unlink()
            print(f"Deleted: {log_file.name}")
    
    print(f"\nCleaned {len(log_files)} log files.")

if __name__ == "__main__":
    print("SwarmBot Log Cleaner")
    print("====================\n")
    
    # For now, just archive logs instead of deleting
    clean_logs(archive=True)
