# MCP Server Management System

## Overview

The MCP (Model Context Protocol) Server Management System provides a comprehensive solution for discovering, installing, testing, and managing MCP servers in the SwarmBot project.

## Components

### 1. Server Inventory (`server_inventory.py`)
- Scans and catalogs configured MCP servers
- Determines server types (Node.js, Python)
- Checks prerequisites (Node.js 16+, Python 3.8+, UV, etc.)
- Validates environment variables

### 2. Prerequisite Installer (`prerequisite_installer.py`)
- Detects missing prerequisites
- Provides installation instructions for each platform
- Attempts automatic installation where possible (e.g., UV via pip)

### 3. Installation Manager (`install_manager.py`)
- Manages server installation process
- Handles both npx and uvx-based servers
- Supports parallel and sequential installation
- Generates installation reports

### 4. Server Manager (`server_manager.py`)
- Manages server lifecycle (start, stop, restart)
- Tracks running processes
- Provides server status information
- Handles graceful shutdown with timeout

## Usage

### Check MCP Server Configuration

```bash
# Windows
scripts\check_mcp_servers.bat

# Or directly with Python
python src/mcp/install_mcp_servers.py --verify
```

### Test Server Inventory

```bash
python tests/mcp/test_inventory.py
```

### Test Complete Management System

```bash
python tests/mcp/test_mcp_management.py
```

## Configuration

Servers are configured in `config/servers_config.json`:

```json
{
  "servers": {
    "server-name": {
      "type": "nodejs|python",
      "command": "npx|uvx|node|python",
      "args": ["arg1", "arg2"],
      "env": {
        "KEY": "value",
        "API_KEY": "${ENV_VAR_NAME}"
      },
      "health_check": {
        "endpoint": "/health",
        "port": 8080,
        "interval": 30
      }
    }
  }
}
```

## Environment Variables

The system supports environment variable placeholders in the format `${VAR_NAME}`:

```json
"env": {
  "GITHUB_TOKEN": "${GITHUB_TOKEN}",
  "API_KEY": "${SOME_API_KEY}"
}
```

These are resolved from the system environment at runtime.

## Server Types

### Node.js Servers (npx)
- Run directly with `npx`
- No local installation required
- Example: `@modelcontextprotocol/server-memory`

### Python Servers (uvx)
- Run with `uvx` (UV package manager)
- No local installation required
- Example: `mcp-server-sqlite`

### Custom Servers
- Any command can be specified
- Supports local scripts and binaries

## Health Checks

Servers can define health check endpoints:

```json
"health_check": {
  "endpoint": "/health",
  "port": 8080,
  "interval": 30,
  "timeout": 5
}
```

## Next Steps

1. **Implement Health Monitoring** (Task 39)
   - Real-time health checks
   - Automatic restart on failure
   - Performance metrics

2. **Add Connection Management** (Task 15)
   - WebSocket/HTTP client connections
   - Connection pooling
   - Retry mechanisms

3. **Integration with SwarmBot** (Task 14)
   - Enhanced mode with auto-tools
   - Seamless MCP server integration
   - Tool discovery and routing

## Troubleshooting

### Prerequisites Not Found
- Ensure Node.js 16+ is installed: `node --version`
- Ensure Python 3.8+ is installed: `python --version`
- Install UV if needed: `pip install uv`

### Environment Variables Missing
- Check your `.env` file
- Ensure variables are exported in your shell
- Use the actual values in config if needed

### Server Won't Start
- Check the command and args in config
- Verify the server package exists
- Check for port conflicts
- Review error logs

## Development

To add a new MCP server:

1. Add configuration to `servers_config.json`
2. Ensure prerequisites are met
3. Run `check_mcp_servers.bat` to verify
4. Start using the server in SwarmBot

## Testing

Run the test suite:

```bash
# Test inventory scanning
python tests/mcp/test_inventory.py

# Test full management
python tests/mcp/test_mcp_management.py

# Run with debug output
python src/mcp/install_mcp_servers.py --verify --debug
```
