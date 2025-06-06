# Quick Fix for main.py Cleanup Issue

## The Problem
The original `main.py` has an async cleanup issue when exiting. The error occurs because tasks are being cancelled in a different context than they were created.

## Quick Solution
For now, use the basic bot (`swarmbot_basic.py`) to verify everything is working. 

## To Fix main.py
If you want to use the original MCP-enabled bot, you can try:

### Option 1: Force Exit (Quick & Dirty)
Add this to the end of main.py:
```python
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nExiting...")
    except Exception as e:
        print(f"\nExiting with error: {e}")
    finally:
        import sys
        sys.exit(0)
```

### Option 2: Proper Cleanup (Recommended)
The issue is in the Server.cleanup() method. The proper fix involves:
1. Ensuring all tasks are cancelled in the same context
2. Using proper exception handling for cancellation
3. Implementing graceful shutdown

### Option 3: Use Different MCP Servers
Try disabling the SQLite server in `servers_config.json`:
```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

## For Now
Use `swarmbot_basic.py` to get started. It's a simpler implementation that:
- Works with your existing Groq API key
- Doesn't have the MCP complexity
- Allows you to verify the basic chat functionality
- Can be evolved later to include MCP features