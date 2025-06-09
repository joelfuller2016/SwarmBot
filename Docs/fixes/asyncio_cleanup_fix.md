# SwarmBot Asyncio Cleanup Fix Documentation

## Issue Description

When SwarmBot exits after certain operations (particularly after listing tools with option 5), two asyncio-related errors appear:

1. `RuntimeError: Event loop is closed` - occurring in `BaseSubprocessTransport.__del__`
2. `ValueError: I/O operation on closed pipe` - occurring in `_ProactorBasePipeTransport.__del__`

These errors are specific to Windows and the ProactorEventLoop (default on Windows).

## Root Cause

The errors occur because:
- SwarmBot creates subprocess transports for MCP servers
- When listing tools, `asyncio.run()` is used which creates its own event loop
- `asyncio.run()` closes the event loop immediately after the coroutine finishes
- Python's garbage collector later tries to clean up the transport objects
- The transport destructors (`__del__` methods) attempt to use the already-closed event loop
- This results in the RuntimeError and ValueError

## Solution Implemented

### 1. Fix for list_tools (Primary Fix)

Added a Windows-specific delay at the end of the `list_tools()` method in `src/core/app.py`:

```python
# Give Windows ProactorEventLoop time to clean up transports
if sys.platform == 'win32':
    await asyncio.sleep(0.5)
```

This gives the ProactorEventLoop time to properly close subprocess transports before `asyncio.run()` closes the event loop.

### 2. Comprehensive Cleanup Method (For Chat Sessions)

Added `_cleanup_event_loop()` method to `SwarmBotApp` class in `src/core/app.py`:

```python
async def _cleanup_event_loop(self, loop) -> None:
    """Comprehensive cleanup of event loop resources to prevent asyncio errors on Windows."""
```

This method:
- Cleanly shuts down all MCP servers
- Cancels all pending tasks
- Provides Windows-specific handling for ProactorEventLoop
- Ensures subprocess transports are closed before the event loop

### 3. Windows-Specific Handling

For Windows systems, the cleanup includes:
- Additional sleep time (0.5s) for subprocess transports to close
- Direct access to loop._transports to force close any remaining transports
- Extra sleep (0.2s) to ensure all I/O operations complete

### 4. Improved Shutdown Sequence

The `finally` block in the `run()` method now:
1. Calls the comprehensive cleanup method
2. Handles any cleanup errors gracefully
3. Only closes the event loop after all resources are released

## Testing

Use the provided test scripts:

```bash
# Test the list_tools fix specifically
python test_list_tools_fix.py

# Test comprehensive cleanup
python test_asyncio_cleanup_fix.py
```

The test scripts:
1. Run SwarmBot with option 5 (list tools) or --list-tools flag
2. Check for asyncio errors in the output
3. Test interrupt handling (Ctrl+C)
4. Report pass/fail status

## Manual Testing

To manually verify the fix:

1. Run SwarmBot: `python swarmbot.py`
2. Select option 5 (List Available Tools)
3. Wait for the tool list to display
4. Press Enter to exit
5. Verify no asyncio errors appear

Or use the command line:
```bash
python swarmbot.py --list-tools
```

## Maintenance Notes

- The fix maintains all existing logging functionality
- No changes to the user interface or features
- The cleanup method is designed to be robust and handle various edge cases
- If new subprocess-based features are added, ensure they integrate with the cleanup system
- The delay in list_tools is only applied on Windows systems

## Related Files

- **Modified**: `src/core/app.py` 
  - Added `_cleanup_event_loop()` method for chat sessions
  - Added Windows-specific delay in `list_tools()` method
- **Existing**: `src/server.py` - Already has proper cleanup in Server class
- **Test**: `test_list_tools_fix.py` - Quick test for the list_tools fix
- **Test**: `test_asyncio_cleanup_fix.py` - Comprehensive test for all scenarios
- **Task**: Taskmaster task #97 tracks this fix

## Future Considerations

1. Consider migrating to `asyncio.run()` for simpler event loop management across all code paths
2. Monitor for similar issues when adding new subprocess-based features
3. The warning suppression in `swarmbot.py` can potentially be removed after thorough testing
4. Consider implementing a custom event loop runner that includes cleanup delays for Windows
