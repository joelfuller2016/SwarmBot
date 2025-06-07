@echo off
echo Running SwarmBot Test Suite...
echo.

:: Move to parent directory
cd ..

:: Run tests
python tests/run_all_tests.py

pause
