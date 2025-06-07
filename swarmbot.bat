@echo off
:: SwarmBot Unified Launcher for Windows
:: Single entry point for all modes

setlocal EnableDelayedExpansion

:: Set console to UTF-8
chcp 65001 > nul 2>&1

:: Set Python to ignore warnings
set PYTHONWARNINGS=ignore::ResourceWarning

:: Check if we're in scripts directory and move to parent
if exist ..\swarmbot.py (
    cd ..
)

:: Check if swarmbot.py exists
if not exist swarmbot.py (
    echo.
    echo ❌ ERROR: swarmbot.py not found!
    echo Please run this script from the SwarmBot directory.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment if it exists
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else if exist .venv\Scripts\activate (
    echo Activating virtual environment...
    call .venv\Scripts\activate
)

:: Display header
echo.
echo ============================================================
echo                 🤖 SwarmBot Launcher
echo ============================================================
echo.

:: Check if arguments were provided
if "%~1"=="" (
    :: No arguments - run interactive mode
    python swarmbot.py
) else (
    :: Pass all arguments to swarmbot.py
    python swarmbot.py %*
)

:: Pause to see any messages
if errorlevel 1 (
    echo.
    echo ❌ SwarmBot exited with an error.
    echo.
)
pause
