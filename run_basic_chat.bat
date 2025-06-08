@echo off
cd /d "C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot"
echo [SwarmBot] Running in standard mode (no MCP servers)...
echo ============================================================
echo.
echo Type 'hello' to test basic chat
echo Type 'quit' to exit
echo.
python swarmbot.py standard --no-validation
