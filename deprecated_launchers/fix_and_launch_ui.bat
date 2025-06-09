@echo off
REM Quick UI Fix Script for SwarmBot Dashboard

echo ===============================================
echo     SwarmBot UI Quick Fix Tool
echo ===============================================
echo.

echo [1] Checking UI Dependencies...
python scripts\check_ui_dependencies.py
if errorlevel 1 (
    echo [ERROR] Dependency check failed!
    pause
    exit /b 1
)

echo.
echo [2] Running UI Diagnostics...
python scripts\diagnose_ui.py
if errorlevel 1 (
    echo [ERROR] Diagnostic check failed!
    echo Please fix the issues listed above.
    pause
    exit /b 1
)

echo.
echo [3] All checks passed! Launching UI...
echo.
python swarmbot.py --ui

pause
