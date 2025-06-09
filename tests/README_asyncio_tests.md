# SwarmBot Asyncio Cleanup Tests

## Overview

These test scripts verify that SwarmBot exits cleanly without asyncio errors on Windows.

## Test Scripts

### test_list_tools_fix.py
Quick test specifically for the list_tools functionality:
```bash
python test_list_tools_fix.py
```

### test_asyncio_cleanup_fix.py
Comprehensive test including interrupt handling:
```bash
python test_asyncio_cleanup_fix.py
```

## What They Test

1. **Clean Exit**: Verifies no `RuntimeError: Event loop is closed` or `ValueError: I/O operation on closed pipe` errors appear
2. **List Tools**: Tests the specific case of listing MCP tools and exiting
3. **Interrupt Handling**: Tests Ctrl+C graceful shutdown (comprehensive test only)

## Expected Results

✅ **PASS**: No asyncio errors in stderr output
❌ **FAIL**: Asyncio errors present in stderr output

## Manual Testing

You can also manually test by running:
```bash
python swarmbot.py --list-tools
```

Or through the launcher:
1. Run `python launch.py`
2. Select option 5 (List Available Tools)
3. Press Enter to continue
4. Check for any error messages

## Notes

- These errors are Windows-specific due to ProactorEventLoop behavior
- The fix adds small delays to allow proper transport cleanup
- Tests should pass on all platforms (non-Windows won't have the errors to begin with)
