@echo off
echo ========================================
echo SwarmBot MCP Server Configuration Check
echo ========================================
echo.

cd /d "%~dp0\.."

python src\mcp\install_mcp_servers.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] MCP configuration check failed
    pause
    exit /b 1
)

echo.
echo [SUCCESS] MCP configuration check completed
pause
