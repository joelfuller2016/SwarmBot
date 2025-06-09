# Config Key Mismatch Fix Documentation

## Issue Summary
When users selected option 5 (List Available Tools) in SwarmBot, they encountered the error:
```
[ERROR] Failed to list tools: 'mcpServers'
```

This occurred because the code expected a key named `mcpServers` in the `servers_config.json` file, but the actual configuration file uses `servers` as the key name.

## Root Cause Analysis
The mismatch was found in multiple files across the codebase:
- `src/core/app.py` (lines 214 and 264)
- `src/ui/dash/integration.py` (line 61)
- `scripts/diagnose_ui.py` (lines 126-129)
- `src/config_validator.py` (line 167 and schema definition)

## Solution Implemented
Implemented backward compatibility to handle both `servers` and `mcpServers` key names. The code now:
1. Checks for the `servers` key first (current standard)
2. Falls back to `mcpServers` if `servers` is not found
3. Handles cases where neither key exists gracefully

### Files Modified

#### 1. src/core/app.py
```python
# Before:
for name, srv_config in server_config['mcpServers'].items():

# After:
servers_dict = server_config.get('servers', server_config.get('mcpServers', {}))
for name, srv_config in servers_dict.items():
```

#### 2. src/ui/dash/integration.py
```python
# Before:
for name, srv_config in server_config.get('mcpServers', {}).items():

# After:
servers_dict = server_config.get('servers', server_config.get('mcpServers', {}))
for name, srv_config in servers_dict.items():
```

#### 3. scripts/diagnose_ui.py
```python
# Before:
if 'mcpServers' in config:
    print(f"✓ Found {len(config['mcpServers'])} MCP servers configured")
else:
    print("✗ No mcpServers section in config")

# After:
servers_dict = config.get('servers', config.get('mcpServers', {}))
if servers_dict:
    print(f"✓ Found {len(servers_dict)} MCP servers configured")
else:
    print("✗ No servers section in config")
```

#### 4. src/config_validator.py
- Updated the iteration logic to handle both keys
- Modified the JSON schema to accept either `servers` or `mcpServers` using `anyOf`

## Testing
Created `tests/test_config_key_fix.py` to verify:
1. Current config structure uses `servers` key
2. List tools functionality works correctly
3. Backward compatibility with `mcpServers` key is maintained

## Benefits
1. **Backward Compatibility**: Existing configurations using `mcpServers` will continue to work
2. **Forward Compatibility**: New configurations using `servers` are fully supported
3. **Graceful Handling**: Clear error messages when neither key is present
4. **No Breaking Changes**: Users don't need to modify their existing configurations

## Verification Steps
To verify the fix:
1. Run `python launch.py` and select option 5 (List Available Tools)
2. Should see the list of configured MCP servers without any errors
3. Test with `python swarmbot.py --list-tools` command
4. Run `python tests/test_config_key_fix.py` to execute automated tests

## Future Considerations
- Consider standardizing on a single key name (`servers`) in future versions
- Add migration script to help users update their configurations
- Update documentation to reflect the preferred key name
