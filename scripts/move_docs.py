#!/usr/bin/env python3
"""Script to organize documentation files into proper subdirectories."""

import os
import shutil
from pathlib import Path

# Define the base directory
BASE_DIR = Path(r"C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot")
DOCS_DIR = BASE_DIR / "Docs"

# Define file categorization
FIX_FILES = [
    "asyncio_cleanup_fix.md",
    "CIRCULAR_IMPORT_FIX.md",
    "CIRCULAR_IMPORT_FIX_DOCUMENTATION.md",
    "CONFIG_KEY_MISMATCH_FIX.md",
    "CRITICAL_FIXES_CHECKLIST.md",
    "DASHBOARD_LAUNCH_QUICK_FIX.md",
    "ERROR_FIXES.md",
    "MCP_NOTIFICATION_FIX.md",
    "TOKEN_TRUNCATION_FIX.md",
    "TOOL_OBJECT_ACCESS_FIX.md",
    "UI_FIX_ACTION_PLAN.md",
    "UI_FIX_IMPLEMENTATION_REPORT.md",
    "UI_FIX_PLAN.md",
    "UI_FIX_SUMMARY.md",
    "UI_LAUNCH_FIX_SUMMARY.md",
    "WEBSOCKET_TEST_FIXES.md",
    "WEBSOCKET_TEST_FIX_DETAILS.md",
    "AUTO_PROMPT_QUICK_FIX_GUIDE.md"
]

GUIDE_FILES = [
    "AUTOMATIC_TOOLS_GUIDE.md",
    "AUTO_PROMPT_GUIDE.md",
    "BASIC_BOT_README.md",
    "How to Add a New MCP Server to SwarmBot.txt",
    "PRIORITY_FEATURES_INTEGRATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "TASKMASTER_GUIDE.md",
    "TESTING_DASHBOARD_PLAN.md",
    "UI_MANUAL_COMPLETE.md",
    "WEBSOCKET_DEPLOYMENT_GUIDE.md",
    "WEBSOCKET_IMPLEMENTATION_GUIDE.md",
    "WEBSOCKET_TROUBLESHOOTING_GUIDE.md"
]

TECHNICAL_FILES = [
    "mcp-server-implementation-doc.md",
    "mcp_server_management.md",
    "swarmbot-realtime-design-doc.md",
    "SWARM_ARCHITECTURE.md",
    "WEBSOCKET_DEPENDENCIES.md",
    "WEBSOCKET_DOCUMENTATION.md",
    "WEBSOCKET_TECHNICAL_REPORT_FINAL.md",
    "WORKFLOW_DIAGRAM.md",
    "CONFIGURATION_ANALYSIS.md",
    "AUTO_PROMPT_TASK_STRUCTURE.md",
    "SWARMBOT_IMPLEMENTATION_SUMMARY.md",
    "UI_IMPLEMENTATION_REQUIREMENTS.md",
    "UI_IMPLEMENTATION_ROADMAP.md"
]

REPORT_FILES = [
    "AUTO_PROMPT_IMPLEMENTATION_SUMMARY.md",
    "AUTO_PROMPT_STATUS_REPORT.md",
    "CLEANUP_SUMMARY.md",
    "DOCUMENTATION_UPDATE_SUMMARY_2025_06_07.md",
    "IMPLEMENTATION_SUMMARY.md",
    "LAUNCHER_MIGRATION.md",
    "LAUNCH_CONSOLIDATION_SUMMARY.md",
    "MCP_INDUSTRY_VALIDATION_REPORT.md",
    "MCP_VERIFICATION_REPORT_2025_06_09.md",
    "MEMORY_UPDATE_COMPLETE.md",
    "PRIORITY_TASKS_IMPLEMENTATION_SUMMARY.md",
    "PROJECT_REVIEW_SUMMARY.md",
    "PROJECT_STATUS_REPORT_2025_06_07.md",
    "PROJECT_UPDATE_2025_06_07_AUTO_PROMPT.md",
    "PROJECT_UPDATE_SUMMARY_2025_06_07.md",
    "PROJECT_UPDATE_SUMMARY_2025_06_07_UI_REVIEW.md",
    "REORGANIZATION_SUMMARY.md",
    "swarmbot-gap-analysis-summary.md",
    "swarmbot-taskmaster-alignment.md",
    "swarmbot-taskmaster-analysis.md",
    "SWARMBOT_VALIDATION_PLAN.md",
    "TASKMASTER_GAP_ANALYSIS_2025_06_07.md",
    "TASKMASTER_WEBSOCKET_STATUS_2025_06_07.md",
    "task_13_code_review_log.md",
    "task_13_final_analysis.md",
    "task_13_implementation_log.md",
    "task_13_user_acceptance_report.md",
    "TASK_7_FILE_ORGANIZATION.md",
    "TASK_7_FINAL_REVIEW_REPORT.md",
    "TASK_7_IMPLEMENTATION_SUMMARY.md",
    "TASK_7_VERIFICATION_PROMPT.md",
    "TASK_ORGANIZATION_SUMMARY.md",
    "UI_IMPLEMENTATION_PROGRESS_2025_06_07.md",
    "UI_IMPLEMENTATION_REVIEW_SUMMARY.md",
    "UI_IMPLEMENTATION_UPDATE_2024_12.md",
    "UI_REVIEW_FINAL_REPORT.md",
    "UI_STATUS_SUMMARY_FINAL.md",
    "UI_TASKS_STATUS_UPDATE.md",
    "UI_TESTING_REPORT_2025_06_07.md",
    "UI_VALIDATION_REPORT_2025_06_07_FINAL.md",
    "VALIDATION_REPORT_2025_06_07.md",
    "WEBSOCKET_IMPLEMENTATION_STATUS_2025_06_07.md",
    "WEBSOCKET_PROGRESS_REPORT_2025_06_07.md",
    "WEBSOCKET_STATUS_REPORT.md",
    "WEBSOCKET_TASK_CREATION_COMPLETE.md",
    "WEBSOCKET_TASK_SUMMARY.md",
    "WEBSOCKET_UPDATE_2025_06_07.md"
]

# Move files to appropriate directories
def move_files(file_list, target_dir):
    """Move files to target directory."""
    moved_count = 0
    for filename in file_list:
        source = DOCS_DIR / filename
        if source.exists():
            dest = DOCS_DIR / target_dir / filename
            try:
                shutil.move(str(source), str(dest))
                print(f"Moved: {filename} -> {target_dir}/")
                moved_count += 1
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            print(f"File not found: {filename}")
    return moved_count

if __name__ == "__main__":
    print("Starting documentation organization...\n")
    
    # Move files to their categories
    fixes_moved = move_files(FIX_FILES, "fixes")
    guides_moved = move_files(GUIDE_FILES, "guides")
    technical_moved = move_files(TECHNICAL_FILES, "technical")
    reports_moved = move_files(REPORT_FILES, "reports")
    
    print(f"\n=== Summary ===")
    print(f"Fixes: {fixes_moved} files moved")
    print(f"Guides: {guides_moved} files moved")
    print(f"Technical: {technical_moved} files moved")
    print(f"Reports: {reports_moved} files moved")
    print(f"Total: {fixes_moved + guides_moved + technical_moved + reports_moved} files moved")
