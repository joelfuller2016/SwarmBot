# MCP Notification Error Fix

## Problem
SwarmBot was showing numerous validation warnings in the console:
```
Failed to validate notification: 13 validation errors for ServerNotification
...
Input should be 'notifications/cancelled' [type=literal_error, input_value='notifications/stderr', input_type=str]
```

These errors occurred because MCP servers were sending `notifications/stderr` messages that the MCP client library couldn't validate against its known notification types.

## Root Cause
- MCP servers send stderr output as notifications with type `notifications/stderr`
- The MCP client library tries to validate these against standard notification types
- Since `notifications/stderr` isn't a recognized type, validation fails for all standard types
- This results in verbose warning logs that clutter the console output

## Solution Implemented

### 1. Created Custom Logging Filter (`src/logging_utils.py`)
- **MCPNotificationFilter**: Filters out MCP notification validation warnings
- **CleanConsoleFormatter**: Provides cleaner console output
- **configure_logging()**: Sets up logging with proper filters and formatters

### 2. Updated Entry Points
- Modified `main.py` and `enhanced_main.py` to use the new logging configuration
- Replaced basic logging setup with custom configuration that includes filters

### 3. Key Features of the Fix
- Suppresses non-critical MCP validation warnings
- Filters out `notifications/stderr` messages
- Maintains all other important log messages
- Cleaner console output for better user experience
- Separate log levels for different components (MCP, pydantic set to ERROR level)

## Benefits
- **Cleaner Output**: No more spam from MCP validation warnings
- **Better UX**: Users see only relevant information
- **Preserved Debugging**: All logs still go to file for troubleshooting
- **Configurable**: Easy to adjust logging levels and filters as needed

## Testing
Run `python tests/test_logging_fix.py` to verify the logging configuration works correctly.

## Note
These warnings were not actual errors - they were just stderr output from MCP servers being misinterpreted as structured notifications. The fix properly filters these out while maintaining all important logging functionality.
