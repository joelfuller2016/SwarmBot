# How to Test SwarmBot Application

## Quick Start Testing Guide

### 1. Initial Setup (5 minutes)
```bash
# Navigate to SwarmBot directory
cd "C:\Users\joelf\OneDrive\Joels Files\Documents\GitHub\SwarmBot"

# Run the universal launcher
python launch.py
```

The launcher will:
- Check Python version (needs 3.8+)
- Install missing dependencies automatically
- Create .env file if missing
- Run diagnostics
- Show interactive menu

### 2. Basic Functionality Tests

#### Test 1: Configuration Validation
From the launch.py menu:
- Choose option 4 (Validate Configuration)
- Check for any ERROR messages
- Ensure at least one API key is configured

#### Test 2: Standard Chat Mode
From the launch.py menu:
- Choose option 3 (Standard Chat)
- Try these commands:
  ```
  You: Hello
  You: What tools are available?
  You: Help
  You: Exit
  ```

#### Test 3: Enhanced Chat Mode
From the launch.py menu:
- Choose option 2 (Enhanced Chat)
- Try these commands:
  ```
  You: Search the web for Python tutorials
  You: Show me all tasks in the project
  You: What's the weather like?
  You: Exit
  ```

#### Test 4: Dashboard UI
From the launch.py menu:
- Choose option 1 (Dashboard UI)
- Browser should open to http://127.0.0.1:8050
- Check:
  - Agent Monitor tab loads
  - Testing Dashboard tab loads
  - Real-time updates work (watch for WebSocket messages in console)
  - No error messages in browser console (F12)

### 3. Component-Specific Tests

#### MCP Tools Test
From chat mode:
```
You: List all available tools
You: Show me active MCP servers
```

#### Taskmaster Test
From chat mode:
```
You: Show all tasks
You: Get task 35
You: What's the project completion percentage?
```

#### Auto-Prompt Test
Start enhanced chat with auto-prompt:
```bash
python swarmbot.py enhanced --auto-prompt --auto-prompt-iterations 3
```
Then give it a multi-step task:
```
You: Create a simple Python function to calculate fibonacci numbers
```
Watch it continue automatically.

### 4. Diagnostic Tests

#### Full System Diagnostics
From launch.py menu:
- Choose option 6 (Run Full Diagnostics)
- Review any failures

#### UI-Specific Diagnostics
```bash
python scripts/diagnose_ui.py
```

#### List Available Tools
From launch.py menu:
- Choose option 5 (List Available Tools)
- Verify MCP servers are loading

### 5. Common Issues to Check

1. **API Keys**: Ensure .env has valid API keys (not "your-xxx-key")
2. **Port 8050**: Make sure nothing else is using port 8050 for dashboard
3. **Dependencies**: All should install automatically, but check for errors
4. **Windows Console**: If you see encoding errors, the launcher should fix them

### 6. Automated Test Suite (Optional)
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_swarmbot_basic.py

# Run with verbose output
python -m pytest tests/ -v
```

### Expected Results

✅ **Working Correctly**:
- Chat responds to commands
- Dashboard opens in browser
- Tools list shows multiple MCP servers
- Tasks display in taskmaster
- No ERROR messages in console

❌ **Known Issues**:
- Dashboard may show import warnings (handled gracefully)
- Some MCP servers may fail to initialize (normal if not configured)
- Windows may show UTF-8 warnings (cosmetic issue)

### Quick Troubleshooting

1. **"No API keys found"**: Edit .env file and add at least one API key
2. **"Import Error"**: Run `pip install -r requirements.txt`
3. **Dashboard won't open**: Try `python scripts/diagnose_ui.py`
4. **Chat not responding**: Check swarmbot.log for errors

### Need Help?

- Check logs in the project directory (swarmbot.log, swarmbot_enhanced.log)
- Run diagnostics: `python launch.py` → Option 6
- Review documentation in the Docs/ directory
