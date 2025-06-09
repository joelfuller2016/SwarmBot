@echo off
echo ==========================================
echo SwarmBot MCP Server Management System Test
echo ==========================================
echo.

cd /d "%~dp0\.."

echo [1] Running MCP Server Configuration Check...
echo.
python src\mcp\install_mcp_servers.py --verify

if errorlevel 1 (
    echo.
    echo [ERROR] Configuration check failed!
    echo Please fix the issues above before proceeding.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [2] Running Full MCP Management Test...
echo ==========================================
echo.

python tests\mcp\test_mcp_management.py

if errorlevel 1 (
    echo.
    echo [ERROR] MCP management test failed!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [SUCCESS] All MCP tests passed!
echo ==========================================
echo.
echo The MCP Server Management System is ready for use.
echo.
echo Next steps:
echo - Run individual servers with the MCPServerManager
echo - Integrate with SwarmBot main application
echo - Implement health monitoring
echo.
pause
